import bcrypt

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Parameters
    ----------
    password : str
        The password to be hashed.
    
    Returns
    -------
    str
        The hashed password.
    """
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """
    Verify a hashed password against a plain password.
    
    Parameters
    ----------
    stored_password : str
        The hashed password stored in the database.
    provided_password : str
        The plain password to verify.
    
    Returns
    -------
    bool
        True if the password is correct, False otherwise.
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

# Brainstorm on do we need to implement the User class
# class User:
#     def __init__(self, username, password, api_key=None):
#         self.username = username
#         self.password = password
#         self.api_key = api_key