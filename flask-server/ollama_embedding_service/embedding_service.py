import os
import json
import requests
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class EmbeddingsService:
    def __init__(self, embeddings_file="attention_index", pdf_directory="./Attention"):
        self.embeddings_file = embeddings_file
        self.pdf_directory = pdf_directory
        self.embeddings = OllamaEmbeddings()
        self.vectors = None

    @st.cache_resource
    def load_or_create_embeddings(self):
        if os.path.exists(self.embeddings_file):
            self._load_existing_embeddings()
        else:
            self._create_new_embeddings()
        return self.vectors

    def _load_existing_embeddings(self):
        self.vectors = FAISS.load_local(self.embeddings_file, self.embeddings, allow_dangerous_deserialization=True)

    def _create_new_embeddings(self):
        loader = PyPDFDirectoryLoader(self.pdf_directory)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_documents = text_splitter.split_documents(docs[:20])
        self.vectors = FAISS.from_documents(final_documents, self.embeddings)
        self.vectors.save_local(self.embeddings_file)
