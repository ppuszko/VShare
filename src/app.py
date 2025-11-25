# uvicorn --host 0.0.0.0 --reload src.app:app
from fastapi import FastAPI, File, UploadFile
from contextlib import asynccontextmanager
from pdfminer.high_level import extract_text
from pathlib import Path
from src.tools import processing
import os
import torch
import asyncio
from sqlmodel import SQLModel
from .config import Config

connection_string = Config.DB_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    
    model = await asyncio.to_thread(processing.load_emb_model, Config.EMB_MODEL)
    app.state.model = model    

    yield

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

app = FastAPI(title="RAG_Agent", description="AI agent utilizing vector database for knowledge-based responses")


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), is_public: bool = False):
    extension = Path(file.filename).suffix.lower()

    safe_filename = os.urandom(8).hex() + extension
    file_path = f"{Config.SAVE_DIR}/{safe_filename}"

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    content = processing.extract_pdf(Path(file_path))
    chunks = processing.create_chunks(content)

    embeddings = processing.get_embedding(app.state.model, chunks)
    print(f"embedding size: {len(embeddings), len(embeddings[0])}, embedding type: {type(embeddings)}")

    return {
        "filename": file.filename,
        "saved_as": safe_filename,
        "content_type": file.content_type,
        "file_extension": extension,
        "chunks size": len(chunks)
    }