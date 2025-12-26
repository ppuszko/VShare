from collections.abc import Iterator
from pathlib import Path
import shutil

import pdfplumber
from odf.opendocument import load
from odf.text import P
from docx import Document
from fastapi import UploadFile
from uuid6 import uuid7

from src.core.config.file import FileConfig
from src.core.db.unit_of_work import UnitOfWork
from src.api.vectors.schemas import DocumentAdd

class FileService:
    def __init__(self, group_uid: str = "", save_path: str = ""):
        dir = Path(save_path)
        self.group_save_dir = dir / group_uid
        self._extractors = {
            "pdf": self._extract_pdf,
            "odt": self._extract_odt,
            "docx": self._extract_docx
        }
        self.allowed_extensions = set(self._extractors.keys())

        
    def save_file(self, file: UploadFile) -> str | None:
        filename = file.filename

        if filename is None:
            return None       
        
        extension = Path(filename).suffix.lstrip(".")
        if extension in self.allowed_extensions:
            file_name = str(uuid7()) + f".{extension}"
            dest = self.group_save_dir / file_name

            with dest.open("wb") as out:
                shutil.copyfileobj(file.file, out)
                return str(dest)
    

    def extract_text_from_files(self, files: list[DocumentAdd]) -> Iterator[tuple[str | None, DocumentAdd]]:
        for file in files:
            if file.storage_path is not None:
                extension = Path(file.storage_path).suffix.lstrip(".")
                extractor = self._extractors.get(extension)
                if extractor is not None:
                    yield extractor(file), file
            else:
                yield None, file


    def _extract_pdf(self, file_path: str | Path) -> str:
        path = Path(file_path) 
        if not path.exists():
            raise FileNotFoundError(path)

        content = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() 
                if text:
                    content.append(text)   
        
        return " ".join(content)


    def _extract_docx(self, file_path: str) -> str:
        path = Path(file_path) 
        if not path.exists():
            raise FileNotFoundError(path)
        
        doc = Document(file_path)
        
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        
        return " ".join(paragraphs)



    def _extract_odt(self, file_path: str | Path) -> str:
        path = Path(file_path) 
        if not path.exists():
            raise FileNotFoundError(path)
        
        doc = load(path)

        content = []
        for p in doc.getElementsByType(P):
            text = "".join(node.data for node in p.childNodes if node.nodeType == 3).strip()
            if text:
                content.append(text)

        return " ".join(content)


                


