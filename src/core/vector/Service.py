from collections.abc import Iterable, Iterator

from qdrant_client import models
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import Request

from main import get_vector_client

class VectorService:

    def __init__(self, request: Request):
        self.dense = request.app.state.dense_model
        self.sparse = request.app.state.sparse_model
        self.mulit = request.app.state.multi_model


    def _split_to_chunks(self, docs: Iterable[Iterable[str | None]]) -> Iterator:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # TODO: rethink whether to pass doc_num or some inserted doc_uid passed to func
        for doc_num, doc in enumerate(docs):
            for page_num, page in enumerate(doc):
                if page:
                    page_chunks = splitter.split_text(page)
                    for chunk in page_chunks:
                        yield (chunk, page_num, doc_num)


    def _compute_vectors(self):
        pass        
