import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_groq import ChatGroq
import re
from db.db import Database
from utils.utils import hash_password, verify_password

class Auth:
    """
    A class to handle user authentication.

    Attributes
    ----------
    conn : psycopg2 connection object
        A connection object to interact with PostgreSQL.
    cursor : psycopg2 cursor object
        A cursor object to perform SQL queries.

    Methods
    -------
    get_api_key(username)
        Retrieves a user's API key from PostgreSQL.
    store_api_key(username, api_key)
        Stores or updates a user's API key in PostgreSQL.
    register_user(username, password)
        Registers a new user in PostgreSQL.
    login(username, password)
        Authenticates a user by verifying their password.
    close()
        Closes the database connection.
    """
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

    def get_api_key(self, username):
        """
        Retrieves a user's API key from PostgreSQL.

        Parameters
        ----------
        username : str
            The username of the user.

        Returns
        -------
        str or None
            The API key of the user, or None if the user does not exist.
        """
        query = """
        SELECT api_key FROM auth.users WHERE username = %s;
        """
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        return result['api_key'] if result else None

    def store_api_key(self, username, api_key):
        """
        Stores or updates a user's API key in PostgreSQL.

        Parameters
        ----------
        username : str
            The username of the user.
        api_key : str
            The API key to be stored or updated.
        """
        query = """
        UPDATE auth.users 
        SET api_key = %s 
        WHERE username = %s;
        """
        self.cursor.execute(query, (api_key, username))
        self.conn.commit()
        print(f"API key for {username} updated successfully.")

    # Method to verify API key by invoking the ChatGroq service
    def verify_api_key(self, api_key, model_name):
        """
        Verify the provided API key by attempting to invoke the ChatGroq service.

        Parameters:
        api_key (str): The API key to be verified.
        model_name (str): The model name to use for the invocation.

        Returns:
        bool: True if the API key is valid; False otherwise.
        """
        try:
            chat = ChatGroq(groq_api_key=api_key, model_name=model_name)
            response = chat.invoke("Test message")
            return True
        except Exception as e:
            print(f"API key verification failed: {e}")
            return False

    def register_user(self, username, password):
        """
        Registers a new user in PostgreSQL.

        Parameters
        ----------
        username : str
            The username of the new user.
        password : str
            The password of the new user.
        """

        # Validate the password
        if not self.is_password_secure(password):
            print("Error: Password does not meet security standards.")
            return

        # Hash the password
        # hashed_password = hash_password(password)

        query = """
        INSERT INTO auth.users (username, password) VALUES (%s, %s);
        """
        try:
            self.cursor.execute(query, (username, password))  # Ensure you hash passwords in production!
            self.conn.commit()
            print(f"User {username} registered successfully.")
        except psycopg2.errors.UniqueViolation:
            print(f"Error: Username '{username}' already exists.")
            self.conn.rollback()  # Rollback the transaction in case of an error
        except psycopg2.Error as e:
            print(f"Error registering user {username}: {e}")

    def is_password_secure(self, password):
            """
            Validates the password against security standards.

            Parameters
            ----------
            password : str
                The password to validate.

            Returns
            -------
            bool
                True if the password is secure, False otherwise.
            """
            # Define password security criteria
            min_length = 8
            has_uppercase = re.search(r'[A-Z]', password) is not None
            has_lowercase = re.search(r'[a-z]', password) is not None
            has_digit = re.search(r'\d', password) is not None
            has_special_char = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None

            # Check password length and criteria
            return (len(password) >= min_length and 
                    has_uppercase and 
                    has_lowercase and 
                    has_digit and 
                    has_special_char)

    def login(self, username, provided_password):
        """
        Authenticates a user by verifying their password.

        Parameters
        ----------
        username : str
            The username of the user.
        password : str
            The password of the user.

        Returns
        -------
        bool
            True if login is successful, False otherwise.
        """
        query = """
        SELECT password FROM auth.users WHERE username = %s;
        """
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        
        # if result and verify_password(result['password'], provided_password):
        if result and result['password'] == provided_password:
            print("Login successful!")
            return True
        else:
            print("Login failed: Invalid username or password.")
            return False

    def close(self):
        """Closes the PostgreSQL connection."""
        self.cursor.close()
        self.conn.close()

# Testing the Auth class functionality
if __name__ == "__main__":
    auth = Auth()
    
    # Register a new user
    auth.register_user("new12", "Sabd.02")  # Replace with hashed password in production

    # Login with the registered user
    auth.login("new", "securepassword")

    # Retrieve API key
    api_key = auth.get_api_key("user")
    print(f"API Key: {api_key}")

    # Store an API key
    auth.store_api_key("new_user1", "example_api_key")

    # Verifying an API key
    model_name = "Llama"
    
    if auth.verify_api_key(api_key, model_name):
        print("API key is valid.")
    else:
        print("Invalid API key.")

    # Close the database connection
    auth.close()
