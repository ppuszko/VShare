# uvicorn --reload src.app:app
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.tools import processing
import torch
import asyncio
from .config import Config, mail_config
from src.errors.exceptions import AppError
from src.groups.routes import group_router
from src.auth.routes import user_router
from itsdangerous import URLSafeTimedSerializer
from fastapi_mail import FastMail

@asynccontextmanager
async def lifespan(app: FastAPI):
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    
    dense_model = await asyncio.to_thread(processing.load_emb_model, Config.DENSE_MODEL)
    app.state.dense_model = dense_model  
    app.state.verify_email_serializer = URLSafeTimedSerializer(Config.JWT_SECRET, salt="verify-email")  
    app.state.fastmail = FastMail(mail_config)

    yield

    if torch.cuda.is_available():
        torch.cuda.empty_cache()


app = FastAPI(
    title="VShare",
    description="Vectorized knowledge bank with group-level access")

app.include_router(group_router, prefix="/groups", tags=["groups"])
app.include_router(user_router, prefix="/user", tags=["users"])


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.detail} 
    )