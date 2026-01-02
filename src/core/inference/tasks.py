import httpx
from httpx import RequestError, HTTPStatusError
from celery import Task
from celery.signals import worker_process_init


from src.core.inference.celery import app
import src.core.inference.celery as global_store
from src.api.vectors.main import init_client, load_dense_model, load_sparse_model, load_multivector_model
from src.api.vectors.service import VectorService
from src.api.vectors.schemas import DocumentAdd
from src.core.utils.file_manager import get_file_man


@worker_process_init.connect
def init_worker(**kwargs):
    global_store.client = init_client()    
    global_store.http_client = httpx.Client(timeout=10.0)

    global_store.dense_model = load_dense_model()
    global_store.sparse_model = load_sparse_model()
    global_store.multi_model = load_multivector_model()


@app.task(autoretry_for=(RequestError, HTTPStatusError), retry_backoff=True)
def send_request(url: str, body: dict | None = None):
    response = global_store.http_client.post(
        url, 
        json=body
    )
    response.raise_for_status()

@app.task
def compute_and_insert_embeddings(files_to_embed: list[DocumentAdd], request_url: str):

    fs = get_file_man()
    documents = fs.extract_text_from_files(files_to_embed)
    
    vector_service = VectorService(global_store.dense_model, 
                                    global_store.sparse_model, 
                                    global_store.multi_model, 
                                    global_store.client)
    documents, emb_counts = vector_service.upload_embeddings(documents)

    body = {
        "documents":documents,
        "emb_counts": emb_counts
    }
    send_request.delay(request_url, body)

