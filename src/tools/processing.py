import pdfplumber
from pathlib import Path
import os
from fastapi import HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer, util


def extract_pdf(file_path: str | Path) -> str | None:
    if not Path.exists(file_path):
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

def create_chunks(document: str) -> list[str] | None:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )

    doc_chunks = text_splitter.create_documents([document])
    chunks = []
    for chunk in doc_chunks:
        chunks.append(str(chunk))

    return chunks

def load_emb_model(model: str) -> object:
    return SentenceTransformer(model)

def get_embedding(model: SentenceTransformer, data: str | list[str]) -> list | None:
    emb = model.encode(data)
    return emb
