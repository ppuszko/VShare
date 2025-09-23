from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from typing import Annotated
from sqlmodel import create_engine, Session, SQLModel
import static_details
from pdfminer.high_level import extract_text
from pathlib import Path
from tools import extractor
import os


connection_string = static_details.DB_CONNECTION_STRING
connect_args = {"check_same_thread": False}
engine = create_engine(connection_string)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def main():
    formatted_content = extract_text("/home/patryk/Downloads/recipe.pdf").replace('\n\n', '<br><br>')

    html_content = f"""
        <html>
            <head>
                <title>My App</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .content {{ line-height: 1.6; }}
                </style>
            </head>
            <body>
                <h1>My Content</h1>
                <div class="content">{formatted_content}</div>
            </body>
        </html>
        """
    return HTMLResponse(content=html_content)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    extension = Path(file.filename).suffix.lower()
    
    

    safe_filename = os.urandom(8).hex() + extension
    file_path = f"{static_details.SAVE_DIR}/{safe_filename}"

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    extractor.extract_pdf(Path(file_path))

    return {
        "filename": file.filename,
        "saved_as": safe_filename,
        "content_type": file.content_type,
        "file_extension": extension
    }