import os
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import digests, news, vectors
from app.services.rag import TextEmbedder


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.backend_api_token = os.environ.get("BACKEND_API_TOKEN")
    # Load RAG config
    config_path = Path(__file__).parent / "config" / "rag_config.yaml"
    with open(config_path) as f:
        rag_config = yaml.safe_load(f)

    app.state.text_embedder = TextEmbedder(
        qdrant_url=settings.QDRANT_URL,
        model_name=rag_config["model"]["name"],
        dimensions=rag_config["model"]["dimensions"],
        quantization=rag_config["model"]["quantization"],
        collection_name=rag_config["search"]["collection_name"],
        distance_metric=rag_config["search"]["distance_metric"],
        default_top_k=rag_config["search"]["default_top_k"],
        max_top_k=rag_config["search"]["max_top_k"],
        qdrant_port=int(os.environ.get("QDRANT_PORT", 6333)),
    )
    await app.state.text_embedder.init_collection()
    yield


app = FastAPI(
    title="News Assistant API",
    description="API news parsing, aggregation, and RAG",
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router, prefix="/api/v1", tags=["news"])
app.include_router(digests.router, prefix="/api/v1/digests", tags=["digests"])
app.include_router(vectors.router, prefix="/api/v1/vectors", tags=["digests"])
