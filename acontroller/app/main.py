import os
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import news, vectors, science
from app.services.rag import TextEmbedder, CommonRAG, OpenAILLM
from app.database import engine
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.state.backend_api_token = os.environ.get("BACKEND_API_TOKEN")
    # Load RAG config
    config_path = Path(__file__).parent / "config" / "public_config.yaml"
    with open(config_path) as f:
        public_config = yaml.safe_load(f)

    app.state.news_embedder = TextEmbedder(
        qdrant_url=settings.QDRANT_URL,
        embedding_model_name=public_config["embedding_model"]["name"],
        dimensions=public_config["embedding_model"]["dimensions"],
        quantization=public_config["embedding_model"]["quantization"],
        collection_name=public_config["rag_search"]["news_collection_name"],
        distance_metric=public_config["rag_search"]["distance_metric"],
        default_top_k=public_config["rag_search"]["default_top_k"],
        max_top_k=public_config["rag_search"]["max_top_k"],
        qdrant_port=int(os.environ.get("QDRANT_PORT", 6333)),
    )
    app.state.science_embedder = TextEmbedder(
        qdrant_url=settings.QDRANT_URL,
        embedding_model_name=public_config["embedding_model"]["name"],
        dimensions=public_config["embedding_model"]["dimensions"],
        quantization=public_config["embedding_model"]["quantization"],
        collection_name=public_config["rag_search"]["science_collection_name"],
        distance_metric=public_config["rag_search"]["distance_metric"],
        default_top_k=public_config["rag_search"]["default_top_k"],
        max_top_k=public_config["rag_search"]["max_top_k"],
        qdrant_port=int(os.environ.get("QDRANT_PORT", 6333)),
    )
    app.state.llm = OpenAILLM(public_config["llm_model"]["name"])
    app.state.rag = CommonRAG(app.state.science_embedder, app.state.news_embedder, app.state.llm)
    await app.state.science_embedder.init_collection()

    await app.state.news_embedder.init_collection()


    await init_db()
    yield
    engine.dispose()

app = FastAPI(
    title="Article Controller",
    description="Article handler and RAG",
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],   #TODO?
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api/v1", tags=["news"])
app.include_router(science.router, prefix="/api/v1", tags=["science"])
app.include_router(vectors.router, prefix="/api/v1", tags=["vectors"])
