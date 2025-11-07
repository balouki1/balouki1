# DevAgent - RAG System for FPDEVSML Generation

DevAgent is a Retrieval Augmented Generation (RAG) system that automatically generates FPDEVSML (Formal Parallel DEVS Modeling Language) specifications from natural language descriptions.

## Overview

DevAgent transforms natural language queries into valid FPDEVSML specifications by:
1. Retrieving relevant examples and documentation from a knowledge base
2. Using an LLM to generate specifications based on the retrieved context
3. Returning structured XML specifications with generation metadata

## Architecture

```
┌─────────────────────┐
│   API FastAPI       │ ← REST Endpoints
└─────────┬───────────┘
          │
     ┌────▼────────────────┐
     │   Orchestrator      │ ← Central Coordination
     └────┬────────────────┘
          │
    ┌─────▼─────────────────────────┐
    │                               │
┌───▼────────┐           ┌──────▼────────┐
│ Retriever  │──────────→│  NL2Spec      │
│   Agent    │           │   Agent       │
└────────────┘           └───────────────┘
     │                          │
     │ FAISS Index              │ LLM (OpenAI/Anthropic)
     │                          ▼
     └──────────────────→ FPDEVSML Spec
```

## Features

- **Semantic Search**: Uses FAISS and sentence transformers for contextual retrieval
- **Multi-LLM Support**: Compatible with OpenAI and Anthropic APIs
- **Async Processing**: Background job processing with status tracking
- **Persistent Storage**: SQLite-based job storage
- **Docker Support**: Containerized deployment with docker-compose
- **Comprehensive Testing**: Unit and integration tests included

## Project Structure

```
devagent/
├── api/                   # FastAPI application
│   ├── main.py            # Entry point & endpoints
│   ├── schemas.py         # Pydantic models
│   └── routes/
├── core/                  # Core business logic
│   ├── orchestrator.py    # Pipeline coordinator
│   ├── retriever.py       # Semantic search agent
│   ├── nl2spec_agent.py   # LLM-based generator
│   └── utils/
│       ├── config.py      # Configuration management
│       ├── logger.py      # Structured logging
│       └── storage.py     # Job persistence
├── data/
│   ├── fpdevsml_examples/ # Example specifications
│   ├── documentation/     # Technical docs
│   └── embeddings/        # FAISS index
└── tests/                 # Test suite
```

## Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)
- OpenAI or Anthropic API key

### Local Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd balouki1
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Set environment variables**
```bash
# Required
export OPENAI_API_KEY=your_key_here
# OR
export ANTHROPIC_API_KEY=your_key_here

# Optional
export LLM_PROVIDER=openai  # or anthropic
export LLM_MODEL=gpt-4-turbo-preview
export LOG_LEVEL=INFO
```

### Docker Installation

1. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

2. **Build and run**
```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

## Usage

### Starting the Server

**Local:**
```bash
python -m uvicorn devagent.api.main:app --reload
```

**Docker:**
```bash
docker-compose up
```

### API Endpoints

#### 1. Submit Natural Language Query

```bash
curl -X POST http://localhost:8000/submit_nl \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Create an M/M/1 queue model with arrival rate 5 and service rate 10"
  }'
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "PENDING",
  "message": "Job submitted successfully"
}
```

#### 2. Check Job Status

```bash
curl http://localhost:8000/status/{job_id}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "SUCCESS",
  "created_at": "2025-11-07T10:30:00.000Z",
  "updated_at": "2025-11-07T10:30:05.000Z"
}
```

#### 3. Get Generated Specification

```bash
curl http://localhost:8000/spec/{job_id}
```

**Response:**
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "SUCCESS",
  "fpdevsml_spec": "<?xml version=\"1.0\"?>\n<model>...</model>",
  "metadata": {
    "retrieval_context": ["atomic_queue.xml", "fpdevsml_guide.md"],
    "generation_time_ms": 1250,
    "model_type": "atomic",
    "llm_provider": "openai",
    "llm_model": "gpt-4-turbo-preview"
  }
}
```

#### 4. Health Check

```bash
curl http://localhost:8000/health
```

### Example Workflow

```bash
# 1. Submit query
JOB_ID=$(curl -X POST http://localhost:8000/submit_nl \
  -H "Content-Type: application/json" \
  -d '{"query": "Create a generator model with exponential distribution"}' \
  | jq -r '.job_id')

# 2. Wait and check status
sleep 3
curl http://localhost:8000/status/$JOB_ID

# 3. Get the generated specification
curl http://localhost:8000/spec/$JOB_ID | jq .
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suites

```bash
# Retriever tests
pytest devagent/tests/test_retriever.py

# NL2Spec tests
pytest devagent/tests/test_nl2spec.py

# End-to-end tests
pytest devagent/tests/test_end_to_end.py
```

### Run with Coverage

```bash
pytest --cov=devagent --cov-report=html
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `LLM_PROVIDER` | LLM provider (openai/anthropic) | `openai` |
| `LLM_MODEL` | Model name | `gpt-4-turbo-preview` |
| `APP_HOST` | Server host | `0.0.0.0` |
| `APP_PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `TOP_K_RESULTS` | Number of retrieval results | `5` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |

### Adding FPDEVSML Examples

Add new examples to `devagent/data/fpdevsml_examples/`:
```bash
# Add XML files
cp your_model.xml devagent/data/fpdevsml_examples/

# Rebuild the index (done automatically on startup)
# Or manually:
# python -c "from devagent.core.retriever import RetrieverAgent; ..."
```

### Adding Documentation

Add technical documentation to `devagent/data/documentation/`:
```bash
cp your_guide.md devagent/data/documentation/
```

The system will automatically index these files on startup.

## Troubleshooting

### Index Not Building

If the FAISS index is not building:
1. Ensure examples exist in `devagent/data/fpdevsml_examples/`
2. Check logs for errors
3. Manually rebuild:
```python
from devagent.core.retriever import RetrieverAgent
agent = RetrieverAgent()
docs = agent.load_documents_from_directory("devagent/data/fpdevsml_examples")
agent.build_index(docs)
```

### LLM Errors

- Verify API keys are set correctly
- Check LLM provider configuration
- Ensure you have sufficient API credits
- Review logs for detailed error messages

### Job Stuck in PENDING

- Check background task logs
- Verify retriever has documents
- Ensure LLM is responding

## Development

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit PR

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Run `black` for formatting

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Limitations

This prototype focuses on the core RAG pipeline. Future versions may include:
- ❌ Lexical/syntactic/semantic validators
- ❌ Specification repair agents
- ❌ Web UI
- ❌ DEVS simulator integration

## License

[Add your license here]

## Contributors

[Add contributors here]

## Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation in `devagent/data/documentation/`

## Changelog

### v1.0.0 (2025-11-07)
- Initial release
- RAG pipeline implementation
- FastAPI backend
- FAISS-based retrieval
- OpenAI/Anthropic LLM support
- Docker deployment
