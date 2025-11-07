# DevAgent - Quick Start Guide

Get DevAgent running in 5 minutes!

## Option 1: Docker (Recommended)

### Prerequisites
- Docker & Docker Compose installed
- OpenAI or Anthropic API key

### Steps

1. **Clone and configure**
```bash
git clone <your-repo-url>
cd balouki1
cp .env.example .env
```

2. **Add your API key to .env**
```bash
# Edit .env and add:
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=your-key-here
```

3. **Start the service**
```bash
docker-compose up --build
```

4. **Test it!**
```bash
# In another terminal
./scripts/test_api.sh
```

That's it! API is running at `http://localhost:8000`

## Option 2: Local Python

### Prerequisites
- Python 3.11+
- pip

### Steps

1. **Clone and setup**
```bash
git clone <your-repo-url>
cd balouki1
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your API key
export OPENAI_API_KEY=sk-your-key-here
```

3. **Start the server**
```bash
python -m uvicorn devagent.api.main:app --reload
```

4. **Test it!**
```bash
# In another terminal
./scripts/test_api.sh
```

## First API Call

### Submit a Query
```bash
curl -X POST http://localhost:8000/submit_nl \
  -H "Content-Type: application/json" \
  -d '{"query": "Create an M/M/1 queue model"}'
```

Response:
```json
{
  "job_id": "abc-123-def-456",
  "status": "PENDING",
  "message": "Job submitted successfully"
}
```

### Get the Result
```bash
# Wait a few seconds, then:
curl http://localhost:8000/spec/abc-123-def-456 | jq .
```

You'll get a generated FPDEVSML specification!

## Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI where you can test the API interactively.

## Common Issues

### "No documents found to index"
Add FPDEVSML examples to `devagent/data/fpdevsml_examples/` and restart.

### "API key not found"
Make sure `.env` file exists and contains your API key.

### Port 8000 already in use
Change the port in `.env` or docker-compose.yml:
```bash
APP_PORT=8001
```

## Next Steps

- Read the full [README.md](README.md)
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Add your own FPDEVSML examples
- Run tests: `pytest`

## Need Help?

- Check logs: `docker-compose logs -f`
- Run tests: `pytest -v`
- Open an issue on GitHub
