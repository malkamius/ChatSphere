import mysql.connector

class IdentityConfig:

    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'chatsphere'
    DB_PASSWORD = 'ChatSphere!'
    DB_NAME = 'chat_sphere_identity'
    
    def get_db_connection(self):
        return mysql.connector.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DB_NAME
        )
        
class IdentityProductionConfig(IdentityConfig):
    DEBUG = False

class IdentityDevelopmentConfig(IdentityConfig):
    DEBUG = True
    
class IdentityTestingConfig(IdentityConfig):
    TESTING = True
    