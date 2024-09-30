# Flask Server Project

This project implements a Flask-based Cybersecurity Auditing Generative Application with RAG (Retrieval-Augmented Generation) capabilities using LangChain, Groq, and Ollama embeddings.

## Project Structure

```
.github/
flask-server/
├── api/
├── llm/
│   └── model.py
├── ollama_embedding_service/
│   ├── Attention/
│   ├── attention_index/
│   ├── __init__.py
│   └── embedding_service.py
├── rag/
│   ├── __init__.py
│   └── rag.py
├── utils/
├── requirements.txt
└── server.py
frontend-v1/
README.md
```

## Components

### 1. LLM Model (`model.py`)

This module implements the ChatAgent class, which handles interactions with the Groq LLM (Language Model).

### 2. Embeddings Service (`embedding_service.py`)

The EmbeddingsService class manages the creation and loading of embeddings using Ollama and FAISS.

Key features:
- Loads existing embeddings or creates new ones from PDF documents
- Uses OllamaEmbeddings for generating embeddings
- Implements caching for improved performance

### 3. RAG (Retrieval-Augmented Generation) (`rag.py`)

The RAG class combines the ChatAgent and EmbeddingsService to provide context-aware responses.

Key features:
- Generates responses based on conversation history and retrieved context
- Handles different conversation stages (initial questions, guidelines, general queries)
- Integrates with the vector store for information retrieval

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/ShelvinPauly/Aegis.git
   cd flask-server
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add necessary API keys and configuration (e.g., `GROQ_API_KEY`)

4. Prepare your document corpus:
   - Place PDF documents in the `ollama_embedding_service/Attention/` directory

5. Run the app:
   ```
   python model.py
   ```

## Usage

The server provides API endpoints for:
- Generating responses using the RAG system
- Managing conversation history
- Handling embeddings and vector store operations

Refer to the API documentation for detailed endpoint information.


