from typing import Any, Dict, List, Optional

import numpy as np
from qdrant_client import models

from .embedders.base import BaseEmbedder, BaseRAG, BaseLLM, BaseMessage
from .embedders.openai import OpenAIEmbedder
from .vector_store import QdrantManager
from openai import AsyncOpenAI, RateLimitError, APIError

import logging
logger = logging.getLogger(__name__)

class TextEmbedder(BaseEmbedder):
    """
    OpenAI-based text embedder that uses Qdrant for vector storage and search.
    """

    def __init__(
        self,
        qdrant_url: str,
        model_name: str,
        dimensions: int,
        quantization: str,
        collection_name: str,
        distance_metric: str,
        default_top_k: int,
        max_top_k: int,
        qdrant_port: int = 6333,
    ):
        """
        Initialize TextEmbedder combining OpenAIEmbedder and QdrantManager.

        :param qdrant_url: Qdrant server URL
        :param model_name: Name of the embedding model
        :param dimensions: Number of dimensions for the embeddings
        :param quantization: Type of quantization to use ("binary" or "none")
        :param collection_name: Name of the Qdrant collection
        :param distance_metric: Distance metric for vector search
        :param qdrant_port: Qdrant server port
        """
        # Initialize Qdrant manager with full config
        self.qdrant_manager = QdrantManager(
            {
                "qdrant_url": qdrant_url,
                "qdrant_port": qdrant_port,
                "model": {"dimensions": dimensions},
                "search": {
                    "collection_name": collection_name,
                    "distance_metric": distance_metric,
                },
            }
        )

        # Initialize OpenAI embedder
        self.embedder = OpenAIEmbedder(
            model_name=model_name, dimensions=dimensions, quantization=quantization
        )

        self.default_top_k = default_top_k
        self.max_top_k = max_top_k

    async def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding using the configured embedder.

        :param text: Input text to embed
        :return: Embedding as numpy array
        """
        return await self.embedder.get_embedding(text)

    async def init_collection(self):
        """Initialize the Qdrant collection if it doesn't exist"""
        await self.qdrant_manager.init_collection()

    async def store_embedding(
        self, text: str, point_id: int, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store embedding in Qdrant using QdrantManager.

        :param text: Text to embed and store
        :param point_id: Unique identifier for the embedding
        :param metadata: Additional metadata to store with the embedding
        """
        embedding = await self.get_embedding(text)
        payload = {"news_id": point_id}  # Only store the news_id
        if metadata:
            payload.update(metadata)

        await self.qdrant_manager.store_embedding(
            point_id=point_id, vector=embedding.tolist(), payload=payload
        )

    async def search_similar(
        self,
        text: str,
        top_k: int = 5,
        filter_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """
        Search for similar texts using QdrantManager.

        :param text: Query text
        :param top_k: Number of results to return
        :param filter_ids: Optional list of ids to filter by
        :return: List of similar documents with scores
        """
        query_embedding = await self.get_embedding(text)
        return await self.qdrant_manager.search_similar(
            vector=query_embedding.tolist(), top_k=top_k, filter_ids=filter_ids
        )


class OpenAIMessage(BaseMessage):
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self):
        return {"role": self.role, "content": self.content}
    
    def to_str(self):
        return f"{self.role}: {self.content}"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(role=data["role"], content=data["content"])


class OpenAILLM(BaseLLM):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.client = AsyncOpenAI()

    async def create_completion(self, chat: List[OpenAIMessage]):
        try:
            completion = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[message.to_dict() for message in chat]
            )
            return completion.choices[0].message
        
        except RateLimitError:
            logger.warning("Rate limit exceeded for OpenAI API")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    
    async def simple_answer(self, prompt: str):
        message = OpenAIMessage(role="user", content=prompt)
        message_out = await self.create_completion([message])
    
        return message_out[0].message['content']
        
    
class NewsRAG(BaseRAG):
    def __init__(self, embedder: TextEmbedder, llm: OpenAILLM, rephrase: bool = True):
        self.embedder = embedder
        self.llm = llm
        self.rephrase = rephrase
        
    def generate_prompt(self, chat_history: List[OpenAIMessage]):
        try:
            with open("prompt_request.txt", "r") as f:
                prompt = f.read()
        except FileNotFoundError as e:
            logger.error(f"Prompt file not found: {e}")
            raise
            
        message_strings = [message.to_str() for message in chat_history]
        prompt += "\n" + "\n".join(message_strings)
        
        return prompt
    
    def generate_rephr_promt(self, chat_history: List[OpenAIMessage]):
        if not chat_history:
            logger.error(f"Chat history is empty")
            raise ValueError()
    
        with open("prompt_rephr.txt", "r") as f:
            rephrase_prompt = f.read()
        rephrase_prompt += "\n"
        rephrase_prompt += chat_history[-1].to_str()
        return rephrase_prompt
    
    async def get_response(self, chat_history: List[OpenAIMessage]):
        ### REPHRASE
        rephrase_prompt = self.generate_rephr_promt(chat_history)
        
        rephrased_request: str = await self.llm.simple_answer(rephrase_prompt)
        
        ### RAG
        rag_prompt = self.generate_prompt(chat_history)  
        response_dict = await self.llm.simple_answer(rag_prompt)
        
        return response_dict
