import pdfplumber
from pathlib import Path

import os
from fastapi import HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
from src.core.config import Config

def extract_pdf(file_path: str | Path) -> str | None:
    if not Path.exists(Path(file_path)):
        raise HTTPException(status_code=400,
                            detail="The file doesn't exist")
    
    content = []
 
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            """tables = page.extract_tables()
            for table in tables:
                for row in table:
                    #print(row)
                    pass"""

            content.append(page.extract_text())
            #print(content[-1])
    
    return "".join(content)

def load_emb_model(model: str) -> object:
    return SentenceTransformer(model)

def create_embedding(model: SentenceTransformer, data: str | list[str]) -> list | None:
    emb = model.encode(data)
    return emb.tolist()

