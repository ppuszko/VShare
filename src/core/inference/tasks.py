from collections.abc import Iterator

from celery.signals import worker_process_init


from src.core.inference.celery import app, dense_model, sparse_model, multi_model
from src.api.vectors.service import VectorService
from src.api.vectors.schemas import DocumentAdd
from src.api.vectors.main import init_client

client = None

@worker_process_init.connect
def instantiate_client():
    global client
    client = init_client()


@app.task
def compute_and_insert_embeddings(files_to_embed: list[DocumentAdd]):
    if client is not None:
        vector = VectorService(dense_model, sparse_model, multi_model, client)

        # TODO: add file records to db and include their id's to text_to_process
        for file in files_to_embed:
            if file.storage_path is not None:

        
    


    # TODO: utilize requests library to send a request to internal endpoint 
    # TODO: create such endpoint
    # TODO: incorporate nginx. Curiosity snippet: 
    """
    how nginx looks like:
    location /internal/ 
        Only allow requests from within the private network (e.g., your docker subnet)
        allow 172.16.0.0/12; 
        allow 127.0.0.1;
        deny all; # Everyone else gets a 403
        
        proxy_pass http://fastapi_app;

    how requests syntax looks like:
    requests.post(
        "http://api-server:8000/internal/notify-completion",
        json=payload,
        headers={"X-Internal-Token": "your-super-long-random-string-here"}
    )
    """