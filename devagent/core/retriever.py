"""Retrieval agent for contextual search in FPDEVSML knowledge base."""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from .utils.logger import get_logger
from .utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class RetrieverAgent:
    """Retrieves relevant FPDEVSML examples and documentation using semantic search."""

    def __init__(
        self,
        embedding_model_name: str = None,
        index_path: Path = None,
        documents_path: Path = None
    ):
        """
        Initialize the retriever agent.

        Args:
            embedding_model_name: Name of the sentence transformer model
            index_path: Path to the FAISS index
            documents_path: Path to the pickled documents
        """
        self.embedding_model_name = embedding_model_name or settings.embedding_model
        self.index_path = index_path or settings.embeddings_path / "faiss.index"
        self.documents_path = documents_path or settings.embeddings_path / "documents.pkl"

        logger.info(
            "Initializing RetrieverAgent",
            model=self.embedding_model_name,
            index_path=str(self.index_path)
        )

        # Load embedding model
        self.encoder = SentenceTransformer(self.embedding_model_name)
        logger.info("Embedding model loaded", model=self.embedding_model_name)

        # Load or create FAISS index
        self.index = None
        self.documents = []

        if self.index_path.exists() and self.documents_path.exists():
            self._load_index()
        else:
            logger.warning("Index not found, will need to build it first")

    def _load_index(self):
        """Load FAISS index and documents from disk."""
        try:
            self.index = faiss.read_index(str(self.index_path))
            with open(self.documents_path, "rb") as f:
                self.documents = pickle.load(f)
            logger.info(
                "Index loaded successfully",
                num_documents=len(self.documents),
                index_size=self.index.ntotal if self.index else 0
            )
        except Exception as e:
            logger.error("Failed to load index", error=str(e))
            raise

    def _save_index(self):
        """Save FAISS index and documents to disk."""
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))
            with open(self.documents_path, "wb") as f:
                pickle.dump(self.documents, f)
            logger.info("Index saved successfully", num_documents=len(self.documents))
        except Exception as e:
            logger.error("Failed to save index", error=str(e))
            raise

    def build_index(self, documents: List[Dict[str, Any]]) -> None:
        """
        Build FAISS index from a list of documents.

        Args:
            documents: List of documents with 'content' and 'source' keys
        """
        logger.info("Building FAISS index", num_documents=len(documents))

        if not documents:
            logger.warning("No documents provided, cannot build index")
            return

        self.documents = documents

        # Extract text content
        texts = [doc["content"] for doc in documents]

        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.encoder.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype(np.float32))

        logger.info(
            "FAISS index built",
            dimension=dimension,
            num_vectors=self.index.ntotal
        )

        # Save index
        self._save_index()

    async def retrieve(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a given query.

        Args:
            query: Natural language query
            top_k: Number of top results to return

        Returns:
            List of dictionaries with 'content', 'source', and 'score' keys
        """
        top_k = top_k or settings.top_k_results

        if not self.index or not self.documents:
            logger.error("Index not initialized or no documents available")
            return []

        logger.info("Retrieving documents", query=query, top_k=top_k)

        # Encode query
        query_embedding = self.encoder.encode(
            [query],
            convert_to_numpy=True
        ).astype(np.float32)

        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, top_k)

        # Prepare results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                # Convert L2 distance to similarity score (normalized)
                score = 1 / (1 + distance)
                results.append({
                    "content": doc["content"],
                    "source": doc["source"],
                    "score": float(score)
                })

        logger.info(
            "Retrieved documents",
            num_results=len(results),
            top_score=results[0]["score"] if results else 0
        )

        return results

    def load_documents_from_directory(
        self,
        directory: Path,
        file_extensions: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Load documents from a directory.

        Args:
            directory: Path to directory containing documents
            file_extensions: List of file extensions to include (e.g., ['.xml', '.txt'])

        Returns:
            List of documents with 'content' and 'source' keys
        """
        file_extensions = file_extensions or ['.xml', '.txt', '.md']
        documents = []

        logger.info("Loading documents from directory", directory=str(directory))

        if not directory.exists():
            logger.warning("Directory does not exist", directory=str(directory))
            return documents

        for ext in file_extensions:
            for file_path in directory.rglob(f"*{ext}"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            documents.append({
                                "content": content,
                                "source": str(file_path.relative_to(directory))
                            })
                except Exception as e:
                    logger.error(
                        "Failed to load document",
                        file=str(file_path),
                        error=str(e)
                    )

        logger.info("Loaded documents", num_documents=len(documents))
        return documents
