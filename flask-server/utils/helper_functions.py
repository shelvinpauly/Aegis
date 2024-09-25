# from langchain.text_splitter import RecursiveCharacterTextSplitter

# def chunk_text(docs, chunk_size=200):
#     # # Split the text by sentences to avoid breaking in the middle of a sentence
#     # sentences = text.split('. ')
#     # chunks = []
#     # current_chunk = ""
#     # for sentence in sentences:
#     #     # Check if adding the next sentence exceeds the chunk size
#     #     if len(current_chunk) + len(sentence) <= chunk_size:
#     #         current_chunk += sentence + '. '
#     #     else:
#     #         # If the chunk reaches the desired size, add it to the chunks list
#     #         chunks.append(current_chunk)
#     #         current_chunk = sentence + '. '
#     # # Add the last chunk if it's not empty
#     # if current_chunk:
#     #     chunks.append(current_chunk)

#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     chunks = text_splitter.split_documents(docs[:20])
#     return chunks

class User:
    def __init__(self, username, password, api_key=None):
        self.username = username
        self.password = password  # This should be hashed
        self.api_key = api_key