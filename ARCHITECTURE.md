# DevAgent Architecture

## System Overview

DevAgent is a RAG (Retrieval Augmented Generation) system designed to generate FPDEVSML specifications from natural language descriptions. The system follows a modular, agent-based architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  (HTTP Clients, cURL, Web Browser, etc.)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    API Layer (FastAPI)                      │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ POST        │  │ GET          │  │ GET          │     │
│  │ /submit_nl  │  │ /status/{id} │  │ /spec/{id}   │     │
│  └─────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  schemas.py - Pydantic Models for Request/Response         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Job Submission
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Orchestration Layer                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Orchestrator                              │  │
│  │  - Coordinates agent workflow                        │  │
│  │  - Manages job lifecycle                             │  │
│  │  - Handles error recovery                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└───────────┬─────────────────────────────┬───────────────────┘
            │                             │
            │                             │
┌───────────▼────────────┐    ┌──────────▼──────────────────┐
│   Retrieval Agent      │    │   NL2Spec Agent             │
│                        │    │                             │
│  ┌──────────────────┐  │    │  ┌───────────────────────┐ │
│  │ Sentence         │  │    │  │ LLM Client            │ │
│  │ Transformer      │  │    │  │ (OpenAI/Anthropic)    │ │
│  │ Encoder          │  │    │  │                       │ │
│  └──────────────────┘  │    │  └───────────────────────┘ │
│                        │    │                             │
│  ┌──────────────────┐  │    │  ┌───────────────────────┐ │
│  │ FAISS Index      │  │    │  │ Prompt Builder        │ │
│  │ (Vector Search)  │  │    │  │                       │ │
│  └──────────────────┘  │    │  └───────────────────────┘ │
│                        │    │                             │
│  ┌──────────────────┐  │    │  ┌───────────────────────┐ │
│  │ Document Store   │  │    │  │ XML Extractor         │ │
│  └──────────────────┘  │    │  └───────────────────────┘ │
└────────────────────────┘    └─────────────────────────────┘
            │                             │
            │                             │
            │    Context               Generated
            │    Documents             Specification
            │                             │
            └─────────────┬───────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                  Storage Layer                            │
│                                                           │
│  ┌────────────────┐    ┌──────────────┐                 │
│  │ SQLite DB      │    │ FAISS Index  │                 │
│  │ (Jobs)         │    │ Files        │                 │
│  └────────────────┘    └──────────────┘                 │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Component Details

### 1. API Layer

**Location**: `devagent/api/`

**Responsibilities**:
- HTTP request handling
- Input validation (Pydantic schemas)
- Background job management
- Response formatting

**Key Files**:
- `main.py`: FastAPI application and endpoints
- `schemas.py`: Request/response models

**Endpoints**:
- `POST /submit_nl`: Submit NL query, returns job_id
- `GET /status/{job_id}`: Get job status
- `GET /spec/{job_id}`: Get generated specification
- `GET /health`: Health check

### 2. Orchestration Layer

**Location**: `devagent/core/orchestrator.py`

**Responsibilities**:
- Coordinate retrieval and generation agents
- Manage job state transitions
- Error handling and recovery
- Metadata aggregation

**Workflow**:
1. Receive job request
2. Update job status to PROCESSING
3. Call RetrieverAgent for context
4. Pass context to NL2SpecAgent
5. Store results
6. Update job status to SUCCESS/FAILED

### 3. Retrieval Agent

**Location**: `devagent/core/retriever.py`

**Responsibilities**:
- Semantic search over knowledge base
- Document indexing and embedding
- Context ranking and filtering

**Components**:
- **Sentence Transformer**: Converts text to embeddings
- **FAISS Index**: Efficient vector similarity search
- **Document Store**: Manages source documents

**Process**:
1. Encode query using sentence transformer
2. Search FAISS index for similar vectors
3. Retrieve top-k documents
4. Return ranked results with scores

### 4. NL2Spec Agent

**Location**: `devagent/core/nl2spec_agent.py`

**Responsibilities**:
- LLM prompt construction
- Specification generation
- XML extraction and validation
- Model type detection

**Components**:
- **LLM Client**: OpenAI or Anthropic client
- **Prompt Builder**: Constructs context-enriched prompts
- **XML Extractor**: Extracts XML from LLM response

**Process**:
1. Build prompt with query + context
2. Call LLM API
3. Extract XML from response
4. Detect model type (atomic/coupled)
5. Return spec with metadata

### 5. Storage Layer

**Location**: `devagent/core/utils/storage.py`

**Responsibilities**:
- Job persistence
- Status tracking
- Result storage

**Schema**:
```sql
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    nl_query TEXT NOT NULL,
    fpdevsml_spec TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

### 6. Utility Layer

**Location**: `devagent/core/utils/`

**Components**:
- `config.py`: Configuration management (Pydantic Settings)
- `logger.py`: Structured logging (structlog)
- `storage.py`: Database operations (aiosqlite)

## Data Flow

### Submission Flow

```
User Request
    ↓
POST /submit_nl
    ↓
Create Job (PENDING)
    ↓
Background Task Started
    ↓
Return job_id to user
```

### Processing Flow

```
Background Task
    ↓
Orchestrator.process_request()
    ↓
Update Status (PROCESSING)
    ↓
RetrieverAgent.retrieve() → Context
    ↓
NL2SpecAgent.generate() → Specification
    ↓
Update Status (SUCCESS) + Store Spec
    ↓
Done
```

### Retrieval Flow

```
GET /status/{job_id}
    ↓
JobStorage.get_job()
    ↓
Return Status Info
```

```
GET /spec/{job_id}
    ↓
JobStorage.get_job()
    ↓
Return Full Spec + Metadata
```

## Design Principles

### 1. Modularity
- Each component has a single responsibility
- Clear interfaces between layers
- Easy to test and maintain

### 2. Async/Await
- Non-blocking I/O operations
- Background job processing
- Efficient resource utilization

### 3. Configurability
- Environment-based configuration
- Support for multiple LLM providers
- Tunable retrieval parameters

### 4. Observability
- Structured logging
- Job status tracking
- Performance metrics in metadata

### 5. Extensibility
- Easy to add new LLM providers
- Pluggable retrieval strategies
- Modular agent architecture

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | FastAPI | REST endpoints |
| Validation | Pydantic | Schema validation |
| Retrieval | FAISS | Vector search |
| Embeddings | Sentence-Transformers | Text encoding |
| LLM | OpenAI/Anthropic | Text generation |
| Storage | SQLite (aiosqlite) | Job persistence |
| Logging | structlog | Structured logging |
| Testing | pytest | Unit/integration tests |
| Deployment | Docker | Containerization |

## Scaling Considerations

### Current Limitations (Prototype)
- Single-process deployment
- In-memory FAISS index
- SQLite database
- Synchronous LLM calls

### Future Improvements
1. **Horizontal Scaling**:
   - Distributed task queue (Celery/RQ)
   - Load balancer for API
   - Shared Redis for job status

2. **Performance**:
   - GPU-accelerated FAISS
   - Batch LLM requests
   - Response caching

3. **Storage**:
   - PostgreSQL for jobs
   - S3 for specifications
   - Redis for caching

4. **Monitoring**:
   - Prometheus metrics
   - Grafana dashboards
   - OpenTelemetry tracing

## Security Considerations

1. **API Keys**: Store securely in environment variables
2. **Input Validation**: Pydantic schemas validate all inputs
3. **Rate Limiting**: Should be added for production
4. **Authentication**: Not implemented (add JWT/OAuth)
5. **CORS**: Currently open (restrict in production)

## Error Handling

### Retrieval Errors
- No context found → Return FAILED status with error message
- Index not built → Log warning, attempt rebuild

### Generation Errors
- LLM API failure → Retry with exponential backoff (future)
- Invalid XML → Return raw response with warning

### Storage Errors
- Database locked → Retry operation
- Disk full → Log critical error

## Testing Strategy

1. **Unit Tests**: Individual components (retriever, nl2spec, storage)
2. **Integration Tests**: End-to-end pipeline
3. **Mocking**: LLM calls mocked for deterministic testing
4. **Fixtures**: Reusable test data and configurations

## Deployment

### Local Development
```bash
uvicorn devagent.api.main:app --reload
```

### Docker
```bash
docker-compose up --build
```

### Production Considerations
- Use gunicorn/uvicorn workers
- Set up reverse proxy (nginx)
- Configure SSL/TLS
- Implement health checks
- Set up monitoring
