# model = ChatGroq(model="llama3-8b-8192")

# store = {}

# prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a cybersecurity auditor. Answer all questions to the best of your ability.",
#         ),
#         MessagesPlaceholder(variable_name="messages"),
#     ]
# )

# chain = prompt | model

# with_message_history = RunnableWithMessageHistory(
#     chain,
#     get_session_history,
#     input_messages_key="messages",
# )

# config = {"configurable": {"session_id": "new"}}

# def get_user_input(prompt, max_length=500):

#   while True:
#     user_input = input(prompt)
#     if len(user_input) <= max_length:
#       return user_input
#     else:
#       print(f"Please enter a string with at most {max_length} characters.")

# response = with_message_history.invoke(
#     {"messages": [HumanMessage(get_user_input("Enter your prompt"))]},
#     config=config,
# )

# response.content

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

#API key to be set

class ChatAgent:
    def __init__(self):
        self.model = ChatGroq(model="llama3-8b-8192")
        self.store = {}
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a cybersecurity auditor. Answer all questions to the best of your ability."),
            MessagesPlaceholder(variable_name="messages"),
        ])
        self.chain = self.prompt | self.model
        self.with_message_history = RunnableWithMessageHistory(
            self.chain, self.get_session_history, input_messages_key="messages"
        )

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
            return self.store[session_id]

    def get_user_input(self, prompt, max_length=500):
        while True:
            user_input = input(prompt)
            if len(user_input) <= max_length:
                return user_input
            else:
                print(f"Please enter a string with at most {max_length} characters.")

    def process_user_input(self, user_input):
        response = self.with_message_history.invoke(
            {"messages": [HumanMessage(user_input)]},
            config={"configurable": {"session_id": "new"}}
        )
        return response

agent = ChatAgent()
user_input = agent.get_user_input("Enter your prompt:")
response = agent.process_user_input(user_input)
print(response)