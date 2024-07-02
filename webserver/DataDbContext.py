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
            cursor.execute("SELECT UUID() AS new_id")
            result = cursor.fetchone()
            # Insert the new request and retrieve the generated UUID
            if result:
                new_uuid = result['new_id']
                # Insert the new request with the generated UUID
                cursor.execute(
                    "INSERT INTO requests (id, session_id, user_id, request_text) VALUES(%s, %s, %s, %s)",
                    (new_uuid, sessionid, userid, request)
                )
                request_id = new_uuid  # Use the generated UUID as the request ID
                connection.commit()
            else:
                raise Exception("Failed to create new UUID")
        except Exception as e:
            self.logger.error(f"Failed to create request for user {userid}: {e}")
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
            cursor.execute("SELECT RIGHT(generated_text, LENGTH(generated_text) - %s) AS generated_text, is_complete, status FROM requests WHERE id = %s AND session_id = %s AND user_id = %s", (skiplength, requestid, sessionid, userid))

            result = cursor.fetchone()
            if result:
                generated_text = result['generated_text']
                if result['is_complete'] and not str.endswith(generated_text, "--end of text--"):
                    generated_text = generated_text + "--end of text--"
            #connection.commit()
        except Exception as e:
            self.logger.error(f"Failed to retrieve message text for user {userid}: {e}")
        finally:
            cursor.close()
            connection.close()
        
        return generated_text
    
    def cancel_request(self, userid: str, sessionid: str):
        connection = self.config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("UPDATE requests SET is_complete = 1, status = 'canceled' WHERE session_id = %s AND user_id= %s AND is_complete = 0",  (sessionid, userid))
            connection.commit()
            return cursor.rowcount > 0
        
        except Exception as e:
            self.logger.error(f"Failed to cancel session {sessionid} for user {userid}: {e}")
            raise e
        finally:
            cursor.close()
            connection.close()
    
    def retrieve_session_requests(self, userid: str, sessionid: str, beforerequestid: str = None, count: int = 10):
        connection = self.config.get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            if beforerequestid != None:
                cursor.execute("""
                                SELECT 
                                    id,
                                    request_text, 
                                    generated_text, 
                                    is_complete, 
                                    status 
                                FROM 
                                    requests
                                WHERE
                                        session_id = %s 
                                    AND user_id= %s 
                                    AND created_at < (  
                                                        SELECT 
                                                            created_at 
                                                        FROM requests 
                                                        WHERE request_id = %s) 
                                ORDER BY created_at DESC LIMIT %s
                               """,  (sessionid, userid, beforerequestid, count))
            else:
                cursor.execute("""
                                SELECT
                                    id, 
                                    request_text, 
                                    generated_text, 
                                    is_complete, 
                                    status 
                                FROM 
                                    requests
                                WHERE
                                        session_id = %s 
                                    AND user_id= %s 
                                ORDER BY created_at DESC LIMIT %s
                               """,  (sessionid, userid, count))
            
            results = cursor.fetchall()
            requests = []
            for row in results:
                request = {'request_id': row['id'], 
                           'request_text': row['request_text'],
                           'generated_text': row['generated_text'],
                           'is_complete': row['is_complete'],
                           'status': row['status']}
                
                requests.insert(0, request)
            return requests                
        except Exception as e:
            self.logger.error(f"Failed to fetch requests for session {sessionid}, user {userid}: {e}")
            raise e
        finally:
            cursor.close()
            connection.close()