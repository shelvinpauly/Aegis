import os
from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
import backoff
import tiktoken
import redis

class RAG:
    def __init__(self, groq_api_key, redis_client):
        self.groq_api_key = groq_api_key
        self.redis_client = redis_client
        self.llm = self.create_llm()
        self.vectors = self.load_or_create_embeddings()

    @backoff.on_exception(backoff.expo, Exception, max_tries=5)
    def create_llm(self):
        return ChatGroq(groq_api_key=self.groq_api_key, model_name="Llama-3.1-70b-Versatile")

    def load_or_create_embeddings(self):
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

    def get_prompt_with_history(self, history, questions_asked):
        conversation_history = "\n".join([f"User: {chat['question']}\nChatbot: {chat['answer']}" for chat in history])
        
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

    def num_tokens_from_string(self, string: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def get_conversation_history(self, session_id):
        history = self.redis_client.lrange(session_id, 0, -1)
        return [eval(item) for item in history]

    def store_chat_history(self, session_id, question, answer):
        self.redis_client.lpush(session_id, str({"question": question, "answer": answer}))

    def generate_response(self, prompt, session_id):
        conversation_history = self.get_conversation_history(session_id)
        questions_asked = len([chat for chat in conversation_history if chat["question"]])
        
        prompt_template = self.get_prompt_with_history(conversation_history, questions_asked)
        document_chain = create_stuff_documents_chain(self.llm, prompt_template)
        retriever = self.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        try:
            response = retrieval_chain.invoke({'input': prompt, 'context': str(conversation_history)})
            reply = response['answer']
            
            self.store_chat_history(session_id, prompt, reply)
            
            return reply, self.num_tokens_from_string(reply)
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                return None, 0
            else:
                raise e