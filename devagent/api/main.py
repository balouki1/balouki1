"""FastAPI application entry point."""

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    SubmitNLRequest,
    SubmitNLResponse,
    JobStatus,
    SpecResponse,
    HealthResponse
)
from devagent.core.orchestrator import Orchestrator
from devagent.core.retriever import RetrieverAgent
from devagent.core.nl2spec_agent import NL2SpecAgent
from devagent.core.utils.storage import JobStorage
from devagent.core.utils.logger import configure_logging, get_logger
from devagent.core.utils.config import get_settings

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)

# Global instances
orchestrator: Orchestrator = None
storage: JobStorage = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator, storage

    logger.info("Starting DevAgent API", version="1.0.0")

    # Initialize storage
    storage = JobStorage()
    await storage.initialize()

    # Initialize retriever
    retriever = RetrieverAgent()

    # Check if index exists, if not, try to build it
    if not retriever.index or not retriever.documents:
        logger.info("Attempting to build index from local documents...")
        # Load from fpdevsml_examples and documentation
        docs = []
        docs.extend(
            retriever.load_documents_from_directory(
                settings.fpdevsml_examples_path,
                file_extensions=['.xml']
            )
        )
        docs.extend(
            retriever.load_documents_from_directory(
                settings.documentation_path,
                file_extensions=['.md', '.txt']
            )
        )

        if docs:
            retriever.build_index(docs)
            logger.info("Index built successfully", num_docs=len(docs))
        else:
            logger.warning("No documents found to build index. Add documents to data directories.")

    # Initialize NL2Spec agent
    nl2spec_agent = NL2SpecAgent()

    # Initialize orchestrator
    orchestrator = Orchestrator(
        retriever=retriever,
        nl2spec_agent=nl2spec_agent,
        storage=storage
    )

    logger.info("DevAgent API started successfully")

    yield

    logger.info("Shutting down DevAgent API")


# Create FastAPI app
app = FastAPI(
    title="DevAgent API",
    description="RAG system for generating FPDEVSML specifications from natural language",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def process_job_background(job_id: str, nl_query: str):
    """Background task to process a job."""
    try:
        await orchestrator.process_request(job_id, nl_query)
    except Exception as e:
        logger.error("Background job processing failed", job_id=job_id, error=str(e))


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/submit_nl", response_model=SubmitNLResponse)
async def submit_nl(
    request: SubmitNLRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a natural language query to generate FPDEVSML specification.

    Args:
        request: Natural language request

    Returns:
        Job submission response with job_id
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())

    logger.info("Received NL submission", job_id=job_id, query=request.query)

    try:
        # Create job in storage
        await storage.create_job(job_id, request.query)

        # Process job in background
        background_tasks.add_task(process_job_background, job_id, request.query)

        return SubmitNLResponse(
            job_id=job_id,
            status="PENDING",
            message="Job submitted successfully"
        )

    except Exception as e:
        logger.error("Failed to submit job", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """
    Get the status of a job.

    Args:
        job_id: Job identifier

    Returns:
        Job status information
    """
    logger.info("Status request", job_id=job_id)

    try:
        status_info = await orchestrator.get_job_status(job_id)

        if not status_info:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobStatus(**status_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job status", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/spec/{job_id}", response_model=SpecResponse)
async def get_spec(job_id: str):
    """
    Get the generated FPDEVSML specification for a job.

    Args:
        job_id: Job identifier

    Returns:
        Complete job information including specification
    """
    logger.info("Spec request", job_id=job_id)

    try:
        job_info = await orchestrator.get_job_spec(job_id)

        if not job_info:
            raise HTTPException(status_code=404, detail="Job not found")

        return SpecResponse(**job_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job spec", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "devagent.api.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
