from collections.abc import Iterable, Iterator

from qdrant_client import models
from langchain_text_splitters import RecursiveCharacterTextSplitter
from fastapi import Request

from src.api.vectors.schemas import EmbModels



class VectorService:

    def __init__(self, models: EmbModels):

        self.dense = models.dense_model
        self.sparse = models.sparse_model
        self.multi = models.multi_model


    def _split_to_chunks(self, docs: Iterable[Iterable[str]]) -> Iterator:
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
                        yield chunk #(, page_num, doc_num)


    def compute_vectors(self, documents: list[Iterable[str]]):
        embeddings = []
        chunks = self._split_to_chunks(documents)

        size = 0

        for chunk in chunks:
            embed = []

            dense_embed = self.dense.encode(chunk)
            size += dense_embed.nbytes

            sparse_embed = next(self.sparse.embed(chunk)).as_object()
            for _, v in sparse_embed.items():
                size +=  len(v) * 8


            multi_embed = next(self.multi.embed(chunk))
            size += multi_embed.nbytes

        return (size / 1000000)
                
