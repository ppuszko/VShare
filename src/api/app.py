# uvicorn --reload src.app:app
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


from src.errors.exceptions import AppError

from src.api.groups.routes import group_router
from src.api.users.routes import user_router
from src.api.vectors.routes import vector_router

from src.core.config.db import DBConfig
from src.core.config.app import AppConfig

from src.core.config.mail import init_mail
from src.core.db.main import init_engine, init_sesssionmaker
from src.core.utils.cache_manager import init_redis
from src.api.vectors.main import (
    init_async_client,
    load_dense_model,
    load_multivector_model,
    load_sparse_model,
    init_vector_collection
)


import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = init_engine(DBConfig.DB_URL)
    app.state.db_engine = engine
    app.state.sessionmaker = init_sesssionmaker(engine)

    vector_client = init_async_client()
    app.state.vector_client = vector_client
    app.state.dense_model = load_dense_model()
    app.state.sparse_model = load_sparse_model()
    app.state.multi_model = load_multivector_model()
    await init_vector_collection(vector_client)

    app.state.redis = init_redis()

    app.state.fastmail = init_mail()

    yield

    await engine.dispose()


app = FastAPI(
    title="VShare",
    description="Vectorized knowledge bank with group level access",
    lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="src/static", html=True), name="static")

app.include_router(group_router, tags=["groups"])
app.include_router(user_router, tags=["users"])
app.include_router(vector_router, tags=["vectors"])

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    traceback.print_exc()
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.detail} 
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    if AppConfig.APP_ENV == "DEV":
        detail = f"Internal error: {str(exc)}"
    else:
        detail = "Oops, Something went worng!"

    return JSONResponse(content={"detail": detail}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
