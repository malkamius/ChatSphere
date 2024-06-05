from .User import User
from shared.identity_db_config import IdentityDevelopmentConfig
import logging
from flask_bcrypt import Bcrypt
from typing import Optional
import uuid

id_config = IdentityDevelopmentConfig()

class UserManager:
    def __init__(self, logger: logging.Logger, bcrypt: Bcrypt):
        self.logger = logger
        self.bcrypt = bcrypt
    def create_user(self, email: str, password: str, confirmation_token: str):
        
        user_id = str(uuid.uuid4())

        user = User(self.bcrypt, user_id, email, email, None, None, True, False, False, confirmation_token)

        user.set_password(password)

        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO aspnetusers (Id, Email, Username, NormalizedEmail, NormalizedUsername, EmailConfirmed, PasswordHash, SecurityStamp, ActivationUUID, PhoneNumberConfirmed) VALUES(%s, %s, %s, UCASE(%s), UCASE(%s), %s, %s, %s, %s, false)",
                (user_id, email, email, email, email, user.email_confirmed, user.password, user.security_stamp, user.confirm_uuid)
            )
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to update user {user.id}: {e}")
        finally:
            cursor.close()
            connection.close()
        return self.get_user(id=user_id)
    
    def update_user(self, user: User):
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "UPDATE aspnetusers SET EmailConfirmed = %s, PasswordHash = %s, SecurityStamp = %s, ActivationUUID = %s WHERE Id = %s",
                (user.email_confirmed, user.password, user.security_stamp, user.confirm_uuid, user.id)
            )
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to update user {user.id}: {e}")
        finally:
            cursor.close()
            connection.close()
    
    def get_user(self, email_address: Optional[str] = None, id: Optional[str] = None) -> User:
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            if id:
                cursor.execute(
                    "SELECT Id, UserName, Email, EmailConfirmed, PasswordHash, SecurityStamp, ActivationUUID, (LockoutEnd IS NULL OR LockoutEnd < CURRENT_TIMESTAMP) = 0 as LockedOut FROM aspnetusers WHERE Id = %s",
                    (id,)
                )
            else:
                cursor.execute(
                    "SELECT Id, UserName, Email, EmailConfirmed, PasswordHash, SecurityStamp, ActivationUUID, (LockoutEnd IS NULL OR LockoutEnd < CURRENT_TIMESTAMP) = 0 as LockedOut FROM aspnetusers WHERE Email = %s",
                    (email_address,)
                )
            user_record = cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Failed to get user by email {email_address}: {e}")
            user_record = None
        finally:
            cursor.close()
            connection.close()

        if user_record:
            return User(
                self.bcrypt,
                user_record["Id"], 
                user_record["UserName"], 
                user_record["Email"], 
                user_record["PasswordHash"], 
                user_record["SecurityStamp"], 
                True, 
                user_record["LockedOut"] != 0, 
                user_record["EmailConfirmed"],
                user_record["ActivationUUID"]
                )
        else:
            return None
        
    def get_user_by_email(self, email_address: str) -> User:
        return self.get_user(email_address=email_address)
            
    def get_user_by_id(self, id: str) -> User:
        return self.get_user(id=id)
            
    def fail_login_attempt(self, user: User):
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "UPDATE aspnetusers SET AccessFailedCount = AccessFailedCount + 1 WHERE Id = %s",
                (user.id,)
            )
            cursor.execute(
                "UPDATE aspnetusers SET LockoutEnd = DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 15 MINUTE) WHERE Id = %s AND AccessFailedCount > 3",
                (user.id,)
            )
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to record failed login attempt for user {user.id}: {e}")
        finally:
            cursor.close()
            connection.close()
        
    def successful_login(self, user: User):
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "UPDATE aspnetusers SET AccessFailedCount = 0 WHERE Id = %s",
                (user.id,)
            )
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to record successful login for user {user.id}: {e}")
        finally:
            cursor.close()
            connection.close()