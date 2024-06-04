from .User import User
from shared.identity_db_config import IdentityDevelopmentConfig

id_config = IdentityDevelopmentConfig()

class UserManager:
    def __init__(self, logger, bcrypt):
        self.logger = logger
        self.bcrypt = bcrypt
    
    def update_user(self, user):
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "UPDATE aspnetusers SET EmailConfirmed = %s, PasswordHash = %s, SecurityStamp = %s WHERE Id = %s",
                (user.email_confirmed, user.password, user.security_stamp, user.id)
            )
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to update user {user.id}: {e}")
        finally:
            cursor.close()
            connection.close()
        
    def get_user_by_email(self, email_address):
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT Id, UserName, Email, EmailConfirmed, PasswordHash, SecurityStamp, (LockoutEnd IS NULL OR LockoutEnd < CURRENT_TIMESTAMP) = 0 as LockedOut FROM aspnetusers WHERE Email = %s",
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
                user_record["EmailConfirmed"]
            )
        else:
            return None
            
    def get_user_by_id(self, id):
        connection = id_config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT Id, UserName, Email, EmailConfirmed, PasswordHash, SecurityStamp, (LockoutEnd IS NULL OR LockoutEnd < CURRENT_TIMESTAMP) = 0 as LockedOut FROM aspnetusers WHERE Id = %s",
                (id,)
            )
            user_record = cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Failed to get user by id {id}: {e}")
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
                user_record["EmailConfirmed"]
            )
        else:
            return None
            
    def fail_login_attempt(self, user):
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
        
    def successful_login(self, user):
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