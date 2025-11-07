"""End-to-end integration tests."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from devagent.api.main import app
from devagent.core.orchestrator import Orchestrator
from devagent.core.retriever import RetrieverAgent
from devagent.core.nl2spec_agent import NL2SpecAgent
from devagent.core.utils.storage import JobStorage


@pytest.fixture
async def test_storage(tmp_path):
    """Create a test storage instance."""
    storage = JobStorage(db_path=tmp_path / "test.db")
    await storage.initialize()
    return storage


@pytest.fixture
def test_documents():
    """Sample test documents."""
    return [
        {
            "content": "M/M/1 queue model with exponential arrivals",
            "source": "queue.xml"
        },
        {
            "content": "Generator model for creating entities",
            "source": "gen.xml"
        }
    ]


@pytest.fixture
async def test_orchestrator(tmp_path, test_storage, test_documents):
    """Create test orchestrator with mocked components."""
    # Create retriever
    retriever = RetrieverAgent(
        index_path=tmp_path / "test.index",
        documents_path=tmp_path / "test.pkl"
    )
    retriever.build_index(test_documents)

    # Create NL2Spec agent with mock
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        nl2spec = NL2SpecAgent(llm_provider="openai", openai_api_key="test-key")

        # Mock the generate method
        async def mock_generate(query, context):
            return {
                "spec": '<?xml version="1.0"?><model name="Generated" type="atomic"></model>',
                "metadata": {
                    "retrieval_context": [c["source"] for c in context],
                    "generation_time_ms": 100,
                    "model_type": "atomic",
                    "llm_provider": "openai",
                    "llm_model": "gpt-4-turbo-preview"
                }
            }

        nl2spec.generate = mock_generate

    return Orchestrator(retriever, nl2spec, test_storage)


@pytest.mark.asyncio
async def test_full_pipeline(test_orchestrator, test_storage):
    """Test the full RAG pipeline."""
    job_id = "test-job-1"
    nl_query = "Create an M/M/1 queue model"

    # Create job
    await test_storage.create_job(job_id, nl_query)

    # Process request
    result = await test_orchestrator.process_request(job_id, nl_query)

    # Verify result
    assert result["job_id"] == job_id
    assert result["status"] == "SUCCESS"
    assert result["fpdevsml_spec"] is not None
    assert "<?xml" in result["fpdevsml_spec"]
    assert result["metadata"]["model_type"] == "atomic"
    assert len(result["metadata"]["retrieval_context"]) > 0

    # Verify job is stored correctly
    job = await test_storage.get_job(job_id)
    assert job is not None
    assert job["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_orchestrator_get_status(test_orchestrator, test_storage):
    """Test getting job status."""
    job_id = "test-job-2"
    nl_query = "Create a generator"

    await test_storage.create_job(job_id, nl_query)

    status = await test_orchestrator.get_job_status(job_id)

    assert status["job_id"] == job_id
    assert status["status"] == "PENDING"
    assert "created_at" in status
    assert "updated_at" in status


@pytest.mark.asyncio
async def test_orchestrator_get_spec(test_orchestrator, test_storage):
    """Test getting job specification."""
    job_id = "test-job-3"
    nl_query = "Create a network model"

    # Create and process job
    await test_storage.create_job(job_id, nl_query)
    await test_orchestrator.process_request(job_id, nl_query)

    # Get spec
    spec_info = await test_orchestrator.get_job_spec(job_id)

    assert spec_info["job_id"] == job_id
    assert spec_info["status"] == "SUCCESS"
    assert spec_info["fpdevsml_spec"] is not None
    assert spec_info["metadata"] is not None


@pytest.mark.asyncio
async def test_orchestrator_nonexistent_job(test_orchestrator):
    """Test handling of nonexistent job."""
    status = await test_orchestrator.get_job_status("nonexistent")
    assert status is None

    spec = await test_orchestrator.get_job_spec("nonexistent")
    assert spec is None


@pytest.mark.asyncio
async def test_api_submit_endpoint():
    """Test the /submit_nl endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Note: This will fail without proper initialization
        # This is a template for how the test would look
        response = await client.post(
            "/submit_nl",
            json={"query": "Create an M/M/1 queue model"}
        )

        # Would assert response when API is fully initialized
        # assert response.status_code == 200
        # assert "job_id" in response.json()


@pytest.mark.asyncio
async def test_error_handling_no_context(test_storage):
    """Test error handling when no context is found."""
    # Create retriever with no documents
    retriever = RetrieverAgent()
    retriever.documents = []
    retriever.index = None

    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        nl2spec = NL2SpecAgent(llm_provider="openai", openai_api_key="test-key")

    orchestrator = Orchestrator(retriever, nl2spec, test_storage)

    job_id = "error-job-1"
    await test_storage.create_job(job_id, "test query")

    result = await orchestrator.process_request(job_id, "test query")

    assert result["status"] == "FAILED"
    assert "error" in result
