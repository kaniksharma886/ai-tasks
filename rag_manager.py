from langchain_core.documents import Document
import os
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config


def get_embedding_model():
    return FastEmbedEmbeddings(model_name=config.EMBEDDING_MODEL)

def get_retriever():
    embeddings = get_embedding_model()
    vector_store = Chroma(persist_directory=config.DB_DIR,
        embedding_function=embeddings,
        collection_name=config.COLLECTION_NAME)
    # Set k=5 to extract the top 5 most relevant results
    return vector_store.as_retriever(search_kwargs={"k": config.TOP_K_RESULTS})


def insert_text(file_paths: list[str]):
    """Chunking of 500 with 20% overlap"""
    embeddings = get_embedding_model()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    processed_documents = []
    
    for path in file_paths:
        if not os.path.exists(path):
            print(f"File ignored :{path}")
            continue

        filename = os.path.basename(path)
        print(f"Reading {filename}")
        with open(path, "r") as f:
            text = f.read()
            
        chunks = text_splitter.split_text(text)
        for idx, chunk in enumerate(chunks):
            processed_documents.append(Document(page_content=chunk, metadata={"source": filename, "chunk_id": idx}))
            
    print(f"Total segments: {len(processed_documents)}.")
    
    batch_size = 1000
    for i in range(0, len(processed_documents), batch_size):
        print(f"Indexing for batch: {i}")
        batch = processed_documents[i:i + batch_size]
        Chroma.from_documents(
            documents=batch,
            embedding=embeddings,
            persist_directory=config.DB_DIR,
            collection_name=config.COLLECTION_NAME
        )
        