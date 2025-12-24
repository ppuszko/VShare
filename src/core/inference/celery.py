from celery import Celery

from src.api.vectors.main import init_client, load_dense_model, load_sparse_model, load_multivector_model

client = init_client()

dense_model = load_dense_model()
sparse_model = load_sparse_model()
multi_model = load_multivector_model()

app = Celery('VShare', 
             broker="redis://localhost", 
             include=["src.core.inference.tasks"],)