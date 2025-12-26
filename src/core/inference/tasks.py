from httpx import RequestError, HTTPStatusError


from src.core.inference.celery import app, dense_model, sparse_model, multi_model, client, http_client
from src.api.vectors.service import VectorService
from src.api.vectors.schemas import DocumentAdd
from src.core.utils.file_service import FileService



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
        fs = FileService()
        documents = fs.extract_text_from_files(files_to_embed)
        
        vector_service = VectorService(dense_model, sparse_model, multi_model, client)
        vector_service.upload_embeddings(documents)

        failed = vector_service.report()
        if len(failed) > 0:
            message = f"Following files hasn't been processed succesfully: {failed}. Currently supported files formats: pdf, odt and docx.\n \
                 Scanned pdf files are currently not supported. If you believe all sent files were following these rules, please try again later."
        else:
            message = "All files processed succesfully"
    else:
        message = "Failed to process files. Please try again later"

    send_request.delay(request_url, message)


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
    """