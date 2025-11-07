"""Tests for NL2SpecAgent."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from devagent.core.nl2spec_agent import NL2SpecAgent


@pytest.fixture
def sample_context():
    """Sample context for testing."""
    return [
        {
            "content": """<?xml version="1.0"?>
<model name="Queue" type="atomic">
  <states>
    <state name="idle" initial="true"/>
    <state name="busy"/>
  </states>
</model>""",
            "source": "queue.xml",
            "score": 0.95
        }
    ]


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response."""
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = """<?xml version="1.0" encoding="UTF-8"?>
<model name="TestModel" type="atomic">
  <description>Generated model</description>
  <ports>
    <input name="in" type="entity"/>
    <output name="out" type="entity"/>
  </ports>
  <states>
    <state name="idle" initial="true"/>
  </states>
</model>"""
    mock_response.choices = [mock_choice]
    return mock_response


@pytest.mark.asyncio
async def test_nl2spec_prompt_building(sample_context):
    """Test that prompt is built correctly."""
    # Use mock to avoid requiring API key
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        agent = NL2SpecAgent(llm_provider="openai", openai_api_key="test-key")

        prompt = agent._build_prompt("Create a simple queue", sample_context)

        assert "Create a simple queue" in prompt
        assert "queue.xml" in prompt
        assert "FPDEVSML" in prompt


@pytest.mark.asyncio
async def test_nl2spec_xml_extraction():
    """Test XML extraction from LLM response."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        agent = NL2SpecAgent(llm_provider="openai", openai_api_key="test-key")

        # Test with full XML
        response = """Here is the model:
<?xml version="1.0"?>
<model name="Test">
</model>
That's the result."""

        xml = agent._extract_xml(response)
        assert xml.startswith("<?xml")
        assert "</model>" in xml


@pytest.mark.asyncio
async def test_nl2spec_model_type_detection():
    """Test model type detection."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        agent = NL2SpecAgent(llm_provider="openai", openai_api_key="test-key")

        atomic_spec = '<model name="Test" type="atomic"></model>'
        assert agent._detect_model_type(atomic_spec) == "atomic"

        coupled_spec = '<model name="Test" type="coupled"></model>'
        assert agent._detect_model_type(coupled_spec) == "coupled"


@pytest.mark.asyncio
async def test_nl2spec_generate_with_mock(sample_context, mock_openai_response):
    """Test generation with mocked OpenAI client."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        agent = NL2SpecAgent(llm_provider="openai", openai_api_key="test-key")

        # Mock the OpenAI client
        agent.client.chat.completions.create = AsyncMock(return_value=mock_openai_response)

        result = await agent.generate("Create a test model", sample_context)

        assert "spec" in result
        assert "metadata" in result
        assert result["metadata"]["model_type"] == "atomic"
        assert result["metadata"]["llm_provider"] == "openai"
        assert result["metadata"]["generation_time_ms"] > 0


@pytest.mark.asyncio
async def test_nl2spec_initialization_validation():
    """Test that initialization validates API keys."""
    with pytest.raises(ValueError):
        # Should raise error if no API key provided
        NL2SpecAgent(llm_provider="openai", openai_api_key="")

    with pytest.raises(ValueError):
        # Should raise error for unsupported provider
        NL2SpecAgent(llm_provider="unsupported", openai_api_key="test-key")
