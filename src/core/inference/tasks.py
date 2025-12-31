from httpx import RequestError, HTTPStatusError


from src.core.inference.celery import app, dense_model, sparse_model, multi_model, client, http_client
from src.api.vectors.service import VectorService
from src.api.vectors.schemas import DocumentAdd
from src.core.utils.file_manager import get_file_man



@app.task(autoretry_for=(RequestError, HTTPStatusError), retry_backoff=True)
def send_request(url: str, body: dict | None = None):
    # 'json=' handles the header and serialization for you
    response = http_client.post(
        url, 
        json=body
    )
    response.raise_for_status()

@app.task
def compute_and_insert_embeddings(files_to_embed: list[DocumentAdd], request_url: str):
    if client is not None:
        fs = get_file_man()
        documents = fs.extract_text_from_files(files_to_embed)
        
        vector_service = VectorService(dense_model, sparse_model, multi_model, client)
        documents, emb_counts = vector_service.upload_embeddings(documents)

    else:
        documents, emb_counts = [], []

    body = {
        "documents":documents,
        "emb_counts": emb_counts
    }
    send_request.delay(request_url, body)


    # TODO: incorporate nginx. Curiosity snippet: 
    """
    how nginx looks like:
    location /internal/ 
        Only allow requests from within the private network (e.g., your docker subnet)
        allow 172.16.0.0/12; 
        allow 127.0.0.1;
        deny all; # Everyone else gets a 403
        
        proxy_pass http://fastapi_app;
    """