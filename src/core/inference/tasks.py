

from src.core.inference.celery import app, emb_models
from src.api.vectors.service import VectorService



@app.task
def get_and_insert_embeddings(files_to_embed: list[str], failed_files: list[str]):
    # TODO: add file records to db and include their id's to text_to_process
    for s in files_to_embed:
        #text_to_process.append(fs.extract_text_from_files(s))
        pass
    vector = VectorService(emb_models)


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