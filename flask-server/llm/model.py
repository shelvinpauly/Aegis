from langchain_groq import ChatGroq
import backoff
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
import os

# before init, make sure you have the env varialbles, if not user needs to set them, so create a route for that too

#develop code to get env variable for .env file (groq api key, etc.)
# Function to verify API key
# groq_api_key is environ var (need to set)
# https://python.langchain.com/v0.2/api_reference/groq/chat_models/langchain_groq.chat_models.ChatGroq.html
def verify_api_key(api_key):
    try:
        chat = ChatGroq(groq_api_key=api_key, model_name="Llama3-70b-8192")
        # response = chat.invoke("Test message")
        return True
    except Exception as e:
        return False
    
# Initialize LLM with retry decorator from langchain_groq import ChatGroq
# llm = ChatGroq(
#     model="mixtral-8x7b-32768",
#     temperature=0.0,
#     max_retries=2,
#     # other params...
# )
@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def create_llm():
    return ChatGroq(groq_api_key, model_name="Llama3-70b-8192")

llm = create_llm()
# Load embeddings at startup
vectors = vectors_db()

# Function to count tokens
def num_tokens_from_string(string: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


# for chunk in llm.stream(messages):
#     print(chunk)
# stream = llm.stream(messages)
# full = next(stream)
# for chunk in stream:
#     full += chunk
def get_prompt_with_history(history, questions_asked):
    conversation_history = "\n".join([f"User: {msg['content']}" if msg['role'] == 'user' else f"Assistant: {msg['content']}" for msg in history])
    
    if questions_asked < 5:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an AI assistant acting as an auditor to help a cybersecurity implementation engineer design the cybersecurity framework for their company using the ISO 27001 and ISO27002 standards.
            You have asked {questions_asked+1} questions so far.

            Conversation history:
            {conversation_history}

            Ask the next most appropriate question to understand the company better. Do not repeat any previous questions.
            The questions should be concise, restricted to one line and should cover only one topic.
            Format your questions as:
            Question {questions_asked+1}: [Your question here]

            Use the context and conversation history to inform your response. Provide the most accurate and relevant information possible.
            """),
            ("human", "Context: {context}\n\nUser Input: {input}")
        ])
    elif questions_asked == 5:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an AI assistant acting as an auditor to help a cybersecurity implementation engineer design the cybersecurity framework for their company using the ISO 27001 and ISO27002 standards.
            You have asked {questions_asked+1} questions so far.

            Conversation history:
            {conversation_history}

            Based on the information provided, here are the key guidelines from ISO27001/ISO27002 for your company's cybersecurity framework:
            [Your comprehensive guidelines here, mention 10 most relevant guidelines] (While answering the guidelines, you should mention which parts/subsections/annex of which document(ISO27001 or ISO27002) you are referencing, be as descriptive as possible)
            Support your answer about each guideline by mentioning how your narrowed your search to that guideline using the information about the company (answers from the user). 

            Use the context and conversation history to inform your response. Provide the most accurate and relevant information possible.
            """),
            ("human", "Context: {context}\n\nUser Input: {input}")
        ])
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are an AI assistant acting as an auditor to answer the user's questions and write code if requested.

            Conversation history:
            {conversation_history}

            The user's question is the last item in the conversation.
            Please answer the user's query based on the information provided in the conversation history, the context, and your knowledge of ISO27001 and ISO27002 standards. Be specific and provide references to the relevant sections of the standards when appropriate.
            """),
            ("human", "Context: {context}\n\nUser Query: {input}")
        ])
    
    return prompt

def load_or_create_embeddings():
    embeddings_file = "faiss_index"
    if os.path.exists(embeddings_file):
        embeddings = OllamaEmbeddings()
        vectors = FAISS.load_local(embeddings_file, embeddings, allow_dangerous_deserialization=True)
    else:
        embeddings = OllamaEmbeddings()
        loader = PyPDFDirectoryLoader("./ISO")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(docs[:20])
        vectors = FAISS.from_documents(final_documents, embeddings)
        vectors.save_local(embeddings_file)
    return vectors