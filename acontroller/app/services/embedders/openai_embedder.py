import os
import logging
from typing import Any, Dict, List, Optional
import backoff
import numpy as np
from openai import AsyncOpenAI, RateLimitError, APIError

logger = logging.getLogger(__name__)
from .base import BaseEmbedder


def binary_quantize(embeddings: np.ndarray) -> np.ndarray:
    """
    Perform binary quantization on embeddings.
    Converts floating point values to binary (0 or 1) based on whether they're above or below the mean.

    :param embeddings: Original embeddings array
    :return: Binary quantized embeddings
    """
    return (embeddings >= np.mean(embeddings)).astype(np.float32)


class OpenAIEmbedder(BaseEmbedder):
    """
    OpenAI-based text embedder that implements BaseEmbedder interface.
    """

    def __init__(
            self,
            model_name: str,
            dimensions: int,
            quantization: str,
            api_base: Optional[str] = None,
    ):
        """
        Initialize OpenAIEmbedder.

        :param model_name: Name of the OpenAI embedding model
        :param dimensions: Number of dimensions for the embeddings
        :param quantization: Type of quantization to use ("binary" or "none")
        :param api_base: Optional custom API base URL
        """
        self.model = model_name
        self.dimensions = dimensions
        self.quantization = quantization
        self.openai_client = AsyncOpenAI()

    @backoff.on_exception(backoff.expo, (RateLimitError, APIError), max_tries=3)
    async def get_embedding(self, text: str) -> np.ndarray:
        """
        Get OpenAI embedding and apply binary quantization if configured.

        :param text: Input text to embed
        :return: Embedding as numpy array
        :raises Exception: If embedding generation fails after retries
        """
        try:
            response = await self.openai_client.with_options(timeout=30.0).embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            embedding = np.array(response.data[0].embedding)
            if self.quantization == "binary":
                return binary_quantize(embedding)
            logger.debug(f"Successfully generated embedding for text: {text[:50]}...")
            return embedding
        except RateLimitError:
            logger.warning("Rate limit exceeded for OpenAI API")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")

    async def store_embedding(
            self, text: str, point_id: int, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store embedding in the vector store.

        Args:
            text: Text to embed and store
            point_id: Unique identifier for the embedding
            metadata: Additional metadata to store with the embedding
        """
        raise NotImplementedError(
            "OpenAIEmbedder should be used with QdrantManager for storage"
        )

    async def search_similar(
            self,
            text: str,
            top_k: int = 5,
            filter_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """
        Search for similar texts using embeddings.

        Args:
            text: Query text
            top_k: Number of results to return
            filter_ids: Optional list of ids to filter by

        Returns:
            List of similar documents with scores
        """
        raise NotImplementedError(
            "OpenAIEmbedder should be used with QdrantManager for search"
        )

    async def init_collection(self):
        """
        Initialize collection - not needed for OpenAIEmbedder as it relies on QdrantManager
        for collection management.
        """
        pass
