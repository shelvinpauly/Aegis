import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json
import datetime

class Database:
    """
    A class to represent the database handler for chat sessions.

    This class handles operations related to PostgreSQL and Redis, ensuring
    that chat sessions are stored in Redis during active conversations
    (volatile memory) and persisted in PostgreSQL for long-term storage
    (non-volatile memory).

    Attributes
    ----------
    conn : psycopg2 connection object
        A connection object to interact with the PostgreSQL database.
    cursor : psycopg2 cursor object
        A cursor object to perform SQL queries on the PostgreSQL database.
    redis_client : redis.StrictRedis
        A Redis client for managing in-memory chat data during active sessions.

    Methods
    -------
    get_postgres_cursor():
        Returns the PostgreSQL cursor for custom queries.
    
    get_redis_client():
        Returns the Redis client for custom queries.

    start_new_session(session_id, username):
        Starts a new chat session in Redis if it doesn't exist in PostgreSQL.
    
    load_existing_session(session_id):
        Loads an existing chat session from PostgreSQL into Redis.
    
    append_message(session_id, message):
        Appends a chat message to Redis for a specified session.

    end_session(session_id, username):
        Syncs chat messages from Redis to PostgreSQL and clears the session from Redis.

    check_session_exists(session_id):
        Checks if a chat session exists in PostgreSQL.

    insert_or_update_chat_session(session_id, username, chat_history):
        Inserts or updates a chat session in PostgreSQL.

    close():
        Closes the PostgreSQL connection.
    """

    def __init__(self):
        """
        Initializes a new instance of the Database class, establishing
        connections to both PostgreSQL and Redis.
        """
        # Initialize the connection to PostgreSQL
        self.conn = psycopg2.connect(
            dbname="aegis_db",
            user="aegis",
            password="aegis_pwd",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

        # Redis setup for storing active chat sessions
        self.redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    def get_postgres_cursor(self):
        """
        Returns the PostgreSQL cursor for performing custom database operations.

        Returns
        -------
        psycopg2 cursor object
            The cursor object for performing SQL queries.
        """
        return self.cursor

    def get_redis_client(self):
        """
        Returns the Redis client for performing custom Redis operations.

        Returns
        -------
        redis.StrictRedis
            The Redis client object.
        """
        return self.redis_client

    def start_new_session(self, session_id, username):
        """
        Starts a new chat session in Redis if it does not exist in PostgreSQL.
        This clears any residual Redis data and prepares Redis for the new session.

        Parameters
        ----------
        session_id : int
            The unique ID for the session.
        username : str
            The username associated with the session.
        """
        # Check if session exists in PostgreSQL
        if not self.check_session_exists(session_id):
            # No session exists, so start a new one in Redis
            self.redis_client.delete(session_id)  # Clear any residual Redis session
            print(f"Starting new session: {session_id} for user {username}")
        else:
            print(f"Session {session_id} already exists. Cannot start a new session with this ID.")

    def load_existing_session(self, session_id):
        """
        Loads an existing chat session from PostgreSQL into Redis for the specified session ID.

        Parameters
        ----------
        session_id : int
            The unique ID of the session to be loaded.
        """
        # Fetch chat history from PostgreSQL
        query = """
        SELECT chat_history FROM chat_history.sessions WHERE session_id = %s;
        """
        self.cursor.execute(query, (session_id,))
        result = self.cursor.fetchone()

        if result:
            chat_history_json = result['chat_history']
            
            # Load chat history from JSON string to a Python list
            try:
                chat_history_list = json.loads(chat_history_json)
            except json.JSONDecodeError:
                print("Error decoding chat history JSON.")
                return
            
            # Push each message from chat history to Redis
            for message in chat_history_list:
                self.redis_client.rpush(session_id, message)
            
            print(f"Loaded session {session_id} into Redis.")
        else:
            print(f"No session found for session_id: {session_id}.")

    def append_message(self, session_id, message):
        """
        Appends a new chat message to Redis for the specified active session.

        Parameters
        ----------
        session_id : int
            The unique ID of the session.
        message : str
            The message to be appended (user or bot message).
        """
        self.redis_client.rpush(session_id, message)
        print(f"Message added to session {session_id}: {message}")

    def end_session(self, session_id, username):
        """
        Ends the chat session by synchronizing chat data from Redis to PostgreSQL
        and clearing the session data from Redis.

        Parameters
        ----------
        session_id : int
            The unique ID of the session.
        username : str
            The username associated with the session.
        """
        # Fetch all chat messages from Redis
        chat_history = self.redis_client.lrange(session_id, 0, -1)

        # Update or insert the session in PostgreSQL
        self.insert_or_update_chat_session(session_id, username, chat_history)

        # Clear Redis for this session
        self.redis_client.delete(session_id)
        print(f"Session {session_id} has been synced and deleted from Redis.")

    def check_session_exists(self, session_id):
        """
        Checks if a session with the specified session ID exists in PostgreSQL.

        Parameters
        ----------
        session_id : int
            The unique ID of the session.

        Returns
        -------
        bool
            True if the session exists, False otherwise.
        """
        query = "SELECT session_id FROM chat_history.sessions WHERE session_id = %s;"
        self.cursor.execute(query, (session_id,))
        return self.cursor.fetchone() is not None

    def insert_or_update_chat_session(self, session_id, username, chat_history):
        """
        Inserts or updates a chat session in PostgreSQL.

        If the session ID already exists, it updates the existing chat history.
        If not, it inserts a new record with the session details.

        Parameters
        ----------
        session_id : int
            The unique ID of the session.
        username : str
            The username associated with the session.
        chat_history : list
            The chat history to be stored (list of messages).
        """
        chat_history = json.dumps(chat_history)  # Convert list to JSON string
        query = """
        INSERT INTO chat_history.sessions (session_id, username, chat_history, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (session_id) DO UPDATE 
        SET chat_history = EXCLUDED.chat_history, updated_at = EXCLUDED.updated_at;
        """
        now = datetime.datetime.utcnow()
        self.cursor.execute(query, (session_id, username, chat_history, now, now))
        self.conn.commit()
        print(f"Session {session_id} saved to PostgreSQL.")

    def close(self):
        """
        Closes the PostgreSQL connection and cursor.
        """
        self.cursor.close()
        self.conn.close()

# Testing the Database class functionality
if __name__ == "__main__":
    db = Database()

    username = "admin"
    session_id = 7

    # If the session is new
    if not db.check_session_exists(session_id):
        db.start_new_session(session_id, username)
    else:
        # If the session exists, load the session from PostgreSQL into Redis
        db.load_existing_session(session_id)

    # Append some messages (user and bot messages) to Redis
    db.append_message(session_id, "User: mast  ?")
    db.append_message(session_id, "Bot: scene bhai scene")

    # End the session and sync chat history from Redis to PostgreSQL
    db.end_session(session_id, username)

    # Close the connection
    db.close()