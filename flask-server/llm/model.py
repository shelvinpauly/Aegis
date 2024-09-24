# can add username and login in this db and table itself
# password and api encryption, decryption need to be pushed to another dir 
# implement api security: encryption, https, freq password change, limiting api usage, dedicated secrets management service

import psycopg2
import redis
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class ChatAgent:
    def __init__(self, username):
        self.username = username

        # Initialize connection to PostgreSQL
        self.conn = psycopg2.connect(
            dbname="aegis_auth",
            user="aegis",
            password="aegis_pwd",
            host="localhost",
            port="5432")
        self.cursor = self.conn.cursor()

        # Initialize Redis connection (port 6379 and db 0 are the default settings)
        self.redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

        # Fetch API key from the DB or prompt user for one
        self.api_key = self.get_api_key_from_db(self.username)
        if not self.api_key:
            self.api_key = self.get_api_key_from_user()
            self.store_api_key_in_db(self.username, self.api_key)

        # Initialize the LLM model (ChatGroq)
        self.model = ChatGroq(model="llama3-8b-8192", api_key=self.api_key)
        self.store = {}
        
        # Prepare the prompt for the chatbot
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a cybersecurity auditor. Answer all questions to the best of your ability."),
            MessagesPlaceholder(variable_name="messages"),
        ])
        self.chain = self.prompt | self.model
        self.with_message_history = RunnableWithMessageHistory(
            self.chain, self.get_session_history, input_messages_key="messages"
        )
    
    # Method to get the API key from the database
    def get_api_key_from_db(self, username):
        self.cursor.execute("SELECT api_key FROM auth.users WHERE username = %s", (username,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    # Research
    # Function to verify API key
    def verify_api_key(self, api_key):
        try:
            chat = ChatGroq(groq_api_key=api_key, model_name="Llama3-70b-8192")
            response = chat.invoke("Test message")
            return True
        except Exception as e:
            return False
    
    # Method to prompt user for their API key if not found in the DB
    def get_api_key_from_user(self):
        for attempt in range(3):
            api_key = input("Please enter your API key: ")
            if self.verify_api_key(api_key):
                self.store_api_key_in_db(self.username, api_key)
                return api_key
            else:
                print("Invalid API key. Please try again.")
        
        raise ValueError("Too many invalid attempts. Please check your API key.")

    # Method to store the API key in the database
    def store_api_key_in_db(self, username, api_key):
        self.cursor.execute("""
        UPDATE auth.users 
        SET api_key = %s 
        WHERE username = %s;
        """, (api_key, username))
        self.conn.commit()

    # Using Redis to store messages keyed by session_id
    def store_chat_history(self, session_id, message):
        self.redis_client.lpush(session_id, message)

    # Method to simulate session-based message history
    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    # Method to prompt user for input, with input length validation
    def get_user_input(self, prompt, max_length=500):
        while True:
            user_input = input(prompt)
            if len(user_input) <= max_length:
                return user_input
            else:
                print(f"Please enter a string with at most {max_length} characters.")

    # Process user input through the chatbot model
    def process_user_input(self, user_input, session_id="new"):
        # Store the user input in Redis
        self.store_chat_history(session_id, f"User: {user_input}")
        
        # Get the response from the chatbot
        response = self.with_message_history.invoke(
            {"messages": [HumanMessage(user_input)]},
            config={"configurable": {"session_id": session_id}}
        )
        
        # Extract and format only the relevant content (excluding metadata)
        response_content = response.content
        
        # Store the response in Redis
        self.store_chat_history(session_id, f"Bot: {response_content}")

        return response_content

# Initialize ChatAgent with username
agent = ChatAgent("admin")

# Loop to hold the conversation
session_id = "user_session_1"  # You can use a unique ID for different sessions
while True:
    user_input = agent.get_user_input("Enter your prompt (or type 'exit' to quit): ")
    
    # Check if the user wants to exit
    if user_input.lower() == "exit":
        print("Ending conversation. Goodbye!")
        break
    
    # Process user input and generate response
    response = agent.process_user_input(user_input, session_id=session_id)
    print(response)