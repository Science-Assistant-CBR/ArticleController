from typing import Any, Dict, List, Optional
import numpy as np
import backoff
import logging
from qdrant_client import models
from qdrant_client.async_qdrant_client import AsyncQdrantClient

logger = logging.getLogger(__name__)


class QdrantManager:
    """
    Manages Qdrant vector store operations including collection management,
    embedding storage, and similarity search.
    """
    def __init__(self, rag_config: dict):
        """
        Initialize QdrantManager from RAG config.

        :param rag_config: Dictionary containing RAG configuration
        """
        search_config = rag_config["search"]
        self.qdrant_client = AsyncQdrantClient(
            url=rag_config["qdrant_url"],
            port=rag_config["qdrant_port"]
        )
        self.collection_name = search_config["collection_name"]
        self.dimensions = rag_config["model"]["dimensions"]
        self.distance_metric = getattr(models.Distance, search_config["distance_metric"])

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def init_collection(self):
        """
        Initialize the Qdrant collection if it doesn't exist.
        
        :raises Exception: If collection initialization fails after retries
        """
        try:
            if not await self.qdrant_client.collection_exists(
                collection_name=self.collection_name
            ):
                await self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.dimensions, distance=self.distance_metric
                    ),
                )
                logger.info(f"Created new collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {str(e)}")
            raise

    async def store_embedding(
        self,
        point_id: int,
        vector: List[float],
        payload: Dict[str, Any],
    ):
        """
        Store an embedding in Qdrant.

        :param point_id: Unique identifier for the embedding
        :param vector: Embedding vector as list of floats
        :param payload: Metadata payload to store with the embedding
        """
        await self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ],
        )

    async def health_check(self) -> bool:
        """
        Check if Qdrant service is healthy.
        
        :return: True if service is healthy, False otherwise
        """
        try:
            await self.qdrant_client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def search_similar(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """
        Search for similar vectors in Qdrant.

        :param vector: Query vector
        :param top_k: Number of results to return
        :param filter_ids: Optional list of ids to filter by
        :return: List of similar documents with scores
        """
        search_params = {
            "collection_name": self.collection_name,
            "query_vector": vector,
            "limit": top_k,
        }

        if filter_ids:
            search_params["query_filter"] = models.Filter(
                must=[
                    models.FieldCondition(
                        key="news_id", match=models.MatchAny(any=filter_ids)
                    )
                ]
            )

        return await self.qdrant_client.search(**search_params)
