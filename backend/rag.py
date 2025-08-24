import os
import glob
import openai
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List
from backend.ingest import load_client_documents, split_text_to_chunks

# Initialize models (load once)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

DATA_DIR = "backend/data"
EMBED_DIR = "backend/embeddings"

# Helper: save/load faiss index and metadata
def save_faiss_index(index, path):
    faiss.write_index(index, path + ".index")

def load_faiss_index(path):
    return faiss.read_index(path + ".index")

def save_metadata(metadata, path):
    import json
    with open(path + ".json", "w") as f:
        json.dump(metadata, f)

def load_metadata(path):
    import json
    with open(path + ".json", "r") as f:
        return json.load(f)

def build_embeddings_for_client(client_id: str):
    # 1. Load all texts for client
    texts = load_client_documents(client_id)
    # 2. Split texts into chunks
    chunks = split_text_to_chunks(texts)
    # 3. Compute embeddings for chunks
    embeddings = embedder.encode(chunks, show_progress_bar=True)
    # 4. Create faiss index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    # 5. Save index and metadata
    client_embed_path = os.path.join(EMBED_DIR, client_id)
    if not os.path.exists(client_embed_path):
        os.makedirs(client_embed_path)
    save_faiss_index(index, os.path.join(client_embed_path, "index"))
    save_metadata(chunks, os.path.join(client_embed_path, "metadata"))

def answer_question(client_id: str, question: str, k=3) -> str:
    """Retrieve relevant chunks and generate answer using OpenAI GPT."""
    client_embed_path = os.path.join(EMBED_DIR, client_id)
    if not os.path.exists(client_embed_path):
        return "No data found for this client. Please upload documents first."

    # Load faiss index and metadata
    index = load_faiss_index(os.path.join(client_embed_path, "index"))
    metadata = load_metadata(os.path.join(client_embed_path, "metadata"))

    # Embed question
    q_emb = embedder.encode([question])
    faiss.normalize_L2(q_emb)

    # Search top k
    D, I = index.search(q_emb, k)
    retrieved_chunks = [metadata[i] for i in I[0]]

    # Build prompt for GPT
    context_text = "\n\n".join(retrieved_chunks)
    prompt = f"You are a helpful assistant. Use the following context to answer the question below:\n\nContext:\n{context_text}\n\nQuestion: {question}\nAnswer:"
    # Call OpenAI API
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=256,
            temperature=0.2,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        answer = response.choices[0].text.strip()
    except Exception as e:
        answer = "Error contacting language model: " + str(e)

    return answer
