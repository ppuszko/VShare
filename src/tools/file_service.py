from collections.abc import Iterator
from pathlib import Path
import shutil


import pdfplumber
from fastapi import UploadFile
from uuid6 import uuid7
from odf.opendocument import load
from odf.text import P
from docx import Document

from src.core.config.file import FileConfig
from src.core.db.unit_of_work import UnitOfWork

class FileService:
    def __init__(self,  uow: UnitOfWork, save_dir: str = ""):
        self.save_dir = Path(save_dir)
        self.allowed_extensions = {ext.strip() for ext in FileConfig.ALLOWED_EXTENSIONS.split(",") if ext.strip()}
        self._session = uow.get_session
        
    def save_files(self, files: list[UploadFile]) -> list[Path]:
        saved_paths = []

        for file in files:
            filename = file.filename
            if filename is None:
                raise FileNotFoundError
            extension = filename.split(".")[-1]

            if extension in self.allowed_extensions:
                file_name = str(uuid7()) + f".{extension}"
                dest = self.save_dir / file_name

                with dest.open("wb") as out:
                    shutil.copyfileobj(file.file, out)
                
                saved_paths.append(dest)
        
            # TODO: implement notification mechanism for all failed files.

        return saved_paths


    def extract_pdf(self, file_path: str | Path) -> Iterator[str | None]:
        path = Path(file_path) 
        if not path.exists():
            raise FileNotFoundError(path)
    
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                yield page.extract_text() 


    def extract_docx(self, file_path: str, min_context_len: int = 1000) -> Iterator[str]:
        path = Path(file_path) 
        if not path.exists():
            raise FileNotFoundError(path)
        
        doc = Document(file_path)
        
        paragraphs = (p.text.strip() for p in doc.paragraphs if p.text.strip())
        
        yield from self._chunk_doc_text(paragraphs, min_context_len)



    def extract_odt(self, file_path: str | Path, min_context_len: int = 1000) -> Iterator[str]:
        path = Path(file_path) 
        if not path.exists():
            raise FileNotFoundError(path)
        
        doc = load(path)

        def iterate_paragraphs():
            for p in doc.getElementsByType(P):
                text = "".join(node.data for node in p.childNodes if node.nodeType == 3).strip()
                if text:
                    yield text

        yield from self._chunk_doc_text(iterate_paragraphs(), min_context_len)
                

    def _chunk_doc_text(self, doc: Iterator[str], min_context_len: int) -> Iterator[str]:
        buffer = []
        buffer_len = 0

        for text in doc:
            text_len = len(text)

            buffer.append(text)
            buffer_len += text_len

            if buffer_len >= min_context_len:
                yield " ".join(buffer)
                buffer = []
                buffer_len = 0
        
        if buffer:
            yield " ".join(buffer)






