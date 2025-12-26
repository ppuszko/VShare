from celery import Celery
from src.api.vectors.main import init_client
from celery.signals import worker_process_init
import httpx

from src.api.vectors.main import init_client, load_dense_model, load_sparse_model, load_multivector_model


app = Celery('VShare', 
             broker="redis://localhost", 
             include=["src.core.inference.tasks"],)

dense_model = load_dense_model()
sparse_model = load_sparse_model()
multi_model = load_multivector_model()

client = None
http_client = None

@worker_process_init.connect
def init_worker():
    global client
    client = init_client()
    global http_client
    http_client = httpx.Client(timeout=10.0)

