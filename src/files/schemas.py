from pydantic import BaseModel 
import uuid
from datetime import datetime
from fastapi import UploadFile


class DocUpload(BaseModel):
    file: UploadFile
    is_public: bool = False
    doc_title: str 