import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import datetime
import redis

class Database:
    def __init__(self):
        # Initialize the connection to the aegis_db
        self.conn = psycopg2.connect(
            dbname="aegis_db",
            user="aegis",
            password="aegis_pwd",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Redis setup
        self.redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    def get_redis_client(self):
        return self.redis_client

    def get_postgres_cursor(self):
        return self.cursor

    # Method to retrieve a user's API key from the database
    def get_api_key(self, username):
        query = """
        SELECT api_key FROM auth.users WHERE username = %s;
        """
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result['api_key'] if result else None

    # Method to store a new API key in the database
    def update_api_key(self, username, api_key):
        query = """
        UPDATE auth.users SET api_key = %s WHERE username = %s;
        """
        self.cursor.execute(query, (api_key, username))
        self.conn.commit()

    # Method to check if a username exists in the database
    def user_exists(self, username):
        query = """
        SELECT id FROM auth.users WHERE username = %s;
        """
        self.cursor.execute(query, (username,))
        return self.cursor.fetchone() is not None

    # Method to insert a new chat session in the chat_history schema
    def insert_chat_session(self, session_id, username, chat_history):
        query = """
        INSERT INTO chat_history.sessions (session_id, username, chat_history, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s);
        """
        now = datetime.datetime.utcnow()
        self.cursor.execute(query, (session_id, username, chat_history, now, now))
        self.conn.commit()

    # Method to update the chat history for an existing session
    def update_chat_session(self, session_id, chat_history):
        query = """
        UPDATE chat_history.sessions
        SET chat_history = %s, updated_at = %s
        WHERE session_id = %s;
        """
        now = datetime.datetime.utcnow()
        self.cursor.execute(query, (chat_history, now, session_id))
        self.conn.commit()

    # Method to retrieve the chat history for a specific session
    def get_chat_history(self, session_id):
        query = """
        SELECT chat_history FROM chat_history.sessions WHERE session_id = %s;
        """
        self.cursor.execute(query, (session_id,))
        result = self.cursor.fetchone()
        return result['chat_history'] if result else None

    def load_chat_history_to_redis(self, session_id):
        # Fetch chat history from PostgreSQL
        self.cursor.execute("SELECT chat_history FROM chat_history.sessions WHERE session_id = %s", (session_id,))
        result = self.cursor.fetchone()
        
        if result:
            chat_history = result[0]  # Assuming chat_history is stored as a text or JSONB column
            # Load into Redis as a list (assuming chat history is a list of messages)
            for message in chat_history:
                self.redis_client.rpush(session_id, message)
        else:
            # Handle case where session_id is not found in the DB
            print(f"No chat history found for session_id: {session_id}")

    def store_chat_in_redis(self, session_id, message):
        self.redis_client.rpush(session_id, message)

    def sync_redis_to_postgres(self, session_id):
        # Fetch chat history from Redis
        chat_history = self.redis_client.lrange(session_id, 0, -1)

        # Update the chat history in PostgreSQL
        self.cursor.execute("""
        UPDATE chat_history.sessions 
        SET chat_history = %s, updated_at = NOW()
        WHERE session_id = %s;
        """, (chat_history, session_id))
        self.conn.commit()

        # Optionally, clear the Redis session data
        self.redis_client.delete(session_id)

    # Close the database connection
    def close(self):
        self.cursor.close()
        self.conn.close()

# Sample
if __name__ == "__main__":
    db = Database()
    
    api_key = db.get_api_key("admin")
    print(api_key)
    
    db.insert_chat_session("2", "admin", "Hello, this is a new session.")
    
    chat_history = db.get_chat_history("2")
    print(chat_history)
    
    db.close()
