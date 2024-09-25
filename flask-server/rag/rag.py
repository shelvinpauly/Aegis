from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
import tiktoken
from ollama_embedding_service.embedding_service import EmbeddingsService
from llm.model import ChatAgent

class RAG:
    def __init__(self, username, embeddings_file="faiss_index", pdf_directory="./ISO"):
        self.chat_agent = ChatAgent(username)
        self.embedding_service = EmbeddingsService(embeddings_file, pdf_directory)
        self.vectors = self.embedding_service.load_or_create_embeddings()

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

    def generate_response(self, prompt, session_id):
        # Use ChatAgent's method to get conversation history
        conversation_history = self.chat_agent.get_session_history(session_id)
        questions_asked = len([chat for chat in conversation_history.messages if chat.type == "human"])
        
        prompt_template = self.get_prompt_with_history(conversation_history.messages, questions_asked)
        document_chain = create_stuff_documents_chain(self.chat_agent.model, prompt_template)
        retriever = self.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        try:
            response = retrieval_chain.invoke({'input': prompt, 'context': str(conversation_history.messages)})
            reply = response['answer']
            
            # Use ChatAgent's method to store chat history
            self.chat_agent.store_chat_history(session_id, f"User: {prompt}")
            self.chat_agent.store_chat_history(session_id, f"Bot: {reply}")
            
            return reply, self.num_tokens_from_string(reply)
        except Exception as e:
            if "rate_limit_exceeded" in str(e):
                return None, 0
            else:
                raise e

# Example usage
# if __name__ == "__main__":
#     rag = RAG("admin")
#     session_id = "user_session_1"
    
#     while True:
#         user_input = rag.chat_agent.get_user_input("Enter your prompt (or type 'exit' to quit): ")
        
#         if user_input.lower() == "exit":
#             print("Ending conversation. Goodbye!")
#             break
        
#         response, _ = rag.generate_response(user_input, session_id)
#         print(response)