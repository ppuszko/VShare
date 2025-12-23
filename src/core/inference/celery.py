from celery import Celery

from src.api.vectors.main import init_client
from src.api.vectors.schemas import EmbModels



client = init_client()
emb_models = EmbModels()

app = Celery('VShare', 
             broker="redis://localhost", 
             include=["src.core.inference.tasks"],)