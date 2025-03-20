import os
from functools import lru_cache
from typing import AsyncGenerator

from miniopy_async import Minio
from app.database import get_db

__all__ = ["get_minio_config", "get_minio", "get_db"]

@lru_cache()
def get_minio_config():
    return {
        "endpoint": os.getenv("MINIO_URL"),
        "access_key": os.getenv("MINIO_ACCESS_KEY"),
        "secret_key": os.getenv("MINIO_SECRET_KEY"),
        "secure": False,
        "bucket_name": os.getenv("MINIO_BUCKET_NAME", "news-assistant-bucket"),
    }


async def get_minio() -> AsyncGenerator[Minio, None]:
    config = get_minio_config()
    client = Minio(
        endpoint=config["endpoint"],
        access_key=config["access_key"],
        secret_key=config["secret_key"],
        secure=config["secure"],
    )

    bucket_exists = await client.bucket_exists(config["bucket_name"])
    if not bucket_exists:
        await client.make_bucket(config["bucket_name"])

    try:
        yield client
    finally:
        pass
