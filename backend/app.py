from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import List, Optional
import asyncio

from rag import build_embeddings_for_client, answer_question

app = FastAPI()

# Allow CORS for local dev (Streamlit -> FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "backend/data"
EMBED_DIR = "backend/embeddings"

class AskRequest(BaseModel):
    client_id: str
    question: str

@app.post("/upload/")
async def upload_files(client_id: str = Form(...), files: List[UploadFile] = File(...)):
    """Upload files for a client, save and generate embeddings."""
    client_folder = os.path.join(DATA_DIR, client_id)
    if not os.path.exists(client_folder):
        os.makedirs(client_folder)
    # Save files
    for file in files:
        file_path = os.path.join(client_folder, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    # Build embeddings async so frontend can get notified once done
    await asyncio.get_event_loop().run_in_executor(None, build_embeddings_for_client, client_id)
    return {"status": "Files uploaded and embeddings created for client " + client_id}

@app.post("/ask/")
async def ask_question(req: AskRequest):
    """Answer a question using client-specific knowledge base."""
    answer = await asyncio.get_event_loop().run_in_executor(None, answer_question, req.client_id, req.question)
    return {"answer": answer}
