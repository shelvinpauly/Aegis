import os
import json
import requests
from langchain_community.embeddings import OllamaEmbeddings

    #check FAISS API
    #Try ollamembedding.embed_documents
vectors = FAISS.from_documents(chunks, OllamaEmbeddings)