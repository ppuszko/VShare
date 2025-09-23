import pdfplumber
from pathlib import Path
import os
from fastapi import HTTPException


def extract_pdf(file_path: str | Path) -> str | None:
    if not Path.exists(file_path):
        raise HTTPException(status_code=400,
                            detail="The file doesn't exist")
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    print(row)

            text = page.extract_text()
            print(text)