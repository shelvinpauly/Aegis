import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import redis
import json

class Database:
    def __init__(self):
        # Initialize the connection to PostgreSQL
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

    # Method to retrieve a user's API key from PostgreSQL
    def get_api_key(self, username):
        query = """
        SELECT api_key FROM auth.users WHERE username = %s;
        """
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result['api_key'] if result else None

    def insert_chat_session(self, session_id, username, chat_history):
        query = """
        INSERT INTO chat_history.sessions (session_id, username, chat_history, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (session_id) DO UPDATE 
        SET chat_history = EXCLUDED.chat_history, updated_at = EXCLUDED.updated_at;
        """
        now = datetime.datetime.utcnow()

        # Ensure that chat_history is in the correct format (e.g., serialized JSON if necessary)
        if isinstance(chat_history, list):
            chat_history = json.dumps(chat_history)

        self.cursor.execute(query, (session_id, username, chat_history, now, now))
        self.conn.commit()

    # Method to retrieve chat history from PostgreSQL
    def get_chat_history(self, session_id):
        query = """
        SELECT chat_history FROM chat_history.sessions WHERE session_id = %s;
        """
        self.cursor.execute(query, (session_id,))
        result = self.cursor.fetchone()
        return result['chat_history'] if result else None

    # Method to load chat history from PostgreSQL into Redis (when session becomes active)
    def load_chat_history_to_redis(self, session_id):
        # Fetch chat history from PostgreSQL
        chat_history = self.get_chat_history(session_id)
        
        if chat_history:
            # Clear existing Redis session data for a clean load
            self.redis_client.delete(session_id)
            
            # Assuming chat_history is a list of messages
            for message in chat_history:
                self.redis_client.rpush(session_id, message)
        # else:
        #     # Handle case where no chat history is found for session_id
        #     print(f"No chat history found for session_id: {session_id}")

    # Method to store a new message in Redis during an active session
    def store_chat_in_redis(self, session_id, message):
        self.redis_client.rpush(session_id, message)

    # Sync chat history from Redis to PostgreSQL (e.g., when the session ends)
    def sync_redis_to_postgres(self, session_id, username):
        # Fetch the entire chat history from Redis
        chat_history = self.redis_client.lrange(session_id, 0, -1)

        if chat_history:
            # Update the chat history in PostgreSQL (replace old with new)
            self.insert_chat_session(session_id, username, chat_history)

        # Optionally clear the Redis session data after syncing
        self.redis_client.delete(session_id)

    def fetch_chat_history_from_redis(self, session_id):
        # Fetch all messages from Redis (list) for the given session_id
        chat_history = self.redis_client.lrange(session_id, 0, -1)
        
        return '\n'.join(chat_history)

    # Method to close the PostgreSQL connection
    def close(self):
        self.cursor.close()
        self.conn.close()

# Sample usage
if __name__ == "__main__":
    db = Database()
    
    username = "admin"
    session_id = 7

    # Fetch and print the API key
    api_key = db.get_api_key(username)
    
    # Load chat history into Redis
    db.load_chat_history_to_redis(session_id)
    # # Fetch and print the updated chat history from Redis
    # chat_history = db.fetch_chat_history_from_redis(session_id)
    # print(f"2. Chat History: {chat_history}")

    # Store a new message in Redis
    db.store_chat_in_redis(session_id, "This is another new message in the session.")
    
    # Fetch and print the updated chat history from Redis
    # chat_history = db.fetch_chat_history_from_redis(session_id)
    # print(f"3. Chat History: {chat_history}")

    # Sync Redis back to PostgreSQL
    db.sync_redis_to_postgres(session_id, username)
    
    # Fetch and print the updated chat history
    # chat_history = db.get_chat_history("2")
    # print(f"Chat History: {chat_history}")
    
    # Close the database connection
    db.close()