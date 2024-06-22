from shared.config import Config
from shared.ansi_logger import getLogger

class DataDbContext:
    config: Config

    def __init__(self, config: Config):
        self.config = config
        self.logger = getLogger(config, __name__)  # Ensure logger is initialized

    def create_new_session(self, userid: str) -> str:
        connection = self.config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        session_id = None
        try:
            # Insert the new session and retrieve the generated UUID
            cursor.execute("INSERT INTO sessions (id, user_id) VALUES(UUID(), %s)", (userid,))
            cursor.execute("SELECT LAST_INSERT_ID() AS session_id")  # Retrieve the last inserted ID
            result = cursor.fetchone()
            if result:
                session_id = result['session_id']
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to create session for user {userid}: {e}")
        finally:
            cursor.close()
            connection.close()
        
        return session_id
    
    def create_new_request(self, userid: str, sessionid: str, request: str):
        connection = self.config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        request_id = None
        try:
            # Insert the new session and retrieve the generated UUID
            cursor.execute("INSERT INTO requests (id, session_id, user_id, request_text) VALUES(UUID(), %s, %s)", (sessionid, userid, request))
            cursor.execute("SELECT LAST_INSERT_ID() AS request_id")  # Retrieve the last inserted ID
            result = cursor.fetchone()
            if result:
                request_id = result['request_id']
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to create session for user {userid}: {e}")
        finally:
            cursor.close()
            connection.close()
        
        return request_id
    
    def get_request_response(self, userid: str, sessionid: str, requestid: str, skiplength: int = 0):
        connection = self.config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        generated_text = None
        try:
            # Insert the new session and retrieve the generated UUID
            cursor.execute("SELECT RIGHT(generated_text, LENGTH(generated_text) - %d) AS generated_text FROM requests WHERE id = %s AND session_id = %s AND user_id = %s", (skiplength, requestid, sessionid, userid))

            result = cursor.fetchone()
            if result:
                generated_text = result['generated_text']
            connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to create session for user {userid}: {e}")
        finally:
            cursor.close()
            connection.close()
        
        return generated_text