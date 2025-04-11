from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import numpy as np


class BaseEmbedder(ABC):
    """
    Abstract base class for all embedders.
    Defines the interface that all embedders must implement.
    """

    @abstractmethod
    async def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for given text.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as numpy array
        """
        pass

    @abstractmethod
    async def store_embedding(
        self, text: str, point_id: int, metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Store embedding in vector store.

        Args:
            text: Text to embed and store
            point_id: Unique identifier for the embedding
            metadata: Optional metadata to store with the embedding
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def init_collection(self):
        """
        Initialize the vector store collection if needed.
        """
        pass


class BaseMessage(ABC): # REVIEW: mb it's an overkill
    """
    Abstract base class for all messages.
    Defines the interface that all messages must implement.
    """
    pass


class BaseLLM(ABC):
    """
    Abstract base class for all LLMs.
    Defines the interface that all LLMs must implement.
    """
    
    @abstractmethod
    async def create_completion(self, chat: list[BaseMessage]) -> str:
        """
        Get completion from LLM.

        Args:
            completion: Input completion

        Returns:
            Response from LLM
        """
        
        pass


class BaseRAG(ABC):
    """
    Abstract base class for all RAG systems.
    Defines the interface that all RAG systems must implement.
    """
    
    def __init__(self, embedder: BaseEmbedder, llm: BaseLLM):
        self.embedder = embedder
        self.llm = llm

        
    @abstractmethod
    async def get_response(self, request: str) -> str:
        """
        Get response from RAG system.

        Args:
            request: Input request

        Returns:
            Response from RAG system
        """
        
        pass
        