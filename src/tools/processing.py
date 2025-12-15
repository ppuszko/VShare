import pdfplumber
from pathlib import Path
from pathlib import Path
from collections.abc import Iterator

def extract_pdf(file_path: str | Path) -> Iterator[str | None]:
    path = Path(file_path) 
    if not path.exists:
        raise FileNotFoundError(path)
 
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            yield page.extract_text() 



