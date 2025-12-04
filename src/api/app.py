# uvicorn --reload src.app:app
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from src.tools import processing
import torch
import asyncio
from src.core.config import Config, mail_config
from src.errors.exceptions import AppError
from src.api.groups.routes import group_router
from src.api.users.routes import user_router
from itsdangerous import URLSafeTimedSerializer
from fastapi_mail import FastMail
from src.core.db.main import init_engine, init_sesssionmaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    
    engine = init_engine(Config.DB_URL)
    app.state.db_engine = engine
    app.state.sessionmaker = init_sesssionmaker(engine)


    dense_model = await asyncio.to_thread(processing.load_emb_model, Config.DENSE_MODEL)
    app.state.dense_model = dense_model  
    app.state.verify_email_serializer = URLSafeTimedSerializer(Config.JWT_SECRET, salt="verify-email")  
    app.state.fastmail = FastMail(mail_config)

    yield

    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    await engine.dispose()


app = FastAPI(
    title="VShare",
    description="Vectorized knowledge bank with group level access",
    lifespan=lifespan)

app.include_router(group_router, prefix="/groups", tags=["groups"])
app.include_router(user_router, prefix="/users", tags=["users"])


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.detail} 
    )