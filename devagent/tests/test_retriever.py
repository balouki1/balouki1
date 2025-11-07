"""Tests for RetrieverAgent."""

import pytest
import asyncio
from pathlib import Path
from devagent.core.retriever import RetrieverAgent


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "content": "This is a model for an M/M/1 queue with exponential arrivals and service times.",
            "source": "mm1_queue.xml"
        },
        {
            "content": "A generator produces entities at regular or random intervals using exponential distribution.",
            "source": "generator.xml"
        },
        {
            "content": "Coupled models connect multiple atomic models through port couplings.",
            "source": "network.xml"
        }
    ]


@pytest.fixture
def retriever(tmp_path, sample_documents):
    """Create a RetrieverAgent with test data."""
    agent = RetrieverAgent(
        index_path=tmp_path / "test.index",
        documents_path=tmp_path / "test.pkl"
    )
    agent.build_index(sample_documents)
    return agent


@pytest.mark.asyncio
async def test_retriever_initialization(retriever):
    """Test that retriever initializes correctly."""
    assert retriever.index is not None
    assert len(retriever.documents) == 3


@pytest.mark.asyncio
async def test_retriever_search(retriever):
    """Test that retriever returns relevant documents."""
    query = "How to create a queue model with arrivals and service?"

    results = await retriever.retrieve(query, top_k=2)

    assert len(results) == 2
    assert all("content" in r for r in results)
    assert all("source" in r for r in results)
    assert all("score" in r for r in results)

    # First result should be about M/M/1 queue
    assert "queue" in results[0]["content"].lower()


@pytest.mark.asyncio
async def test_retriever_empty_query(retriever):
    """Test retriever with empty results."""
    # This should still return results, but with lower scores
    query = "xyz123notfound"

    results = await retriever.retrieve(query, top_k=1)

    assert len(results) == 1
    assert results[0]["score"] > 0


@pytest.mark.asyncio
async def test_build_and_save_index(tmp_path, sample_documents):
    """Test that index can be built and saved."""
    agent = RetrieverAgent(
        index_path=tmp_path / "saved.index",
        documents_path=tmp_path / "saved.pkl"
    )

    agent.build_index(sample_documents)

    assert (tmp_path / "saved.index").exists()
    assert (tmp_path / "saved.pkl").exists()


@pytest.mark.asyncio
async def test_load_existing_index(tmp_path, sample_documents):
    """Test that index can be loaded from disk."""
    # First, create and save an index
    agent1 = RetrieverAgent(
        index_path=tmp_path / "saved.index",
        documents_path=tmp_path / "saved.pkl"
    )
    agent1.build_index(sample_documents)

    # Then, load it in a new instance
    agent2 = RetrieverAgent(
        index_path=tmp_path / "saved.index",
        documents_path=tmp_path / "saved.pkl"
    )

    assert len(agent2.documents) == 3
    assert agent2.index.ntotal == 3
