"""Pydantic models for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class SubmitNLRequest(BaseModel):
    """Request model for natural language submission."""

    query: str = Field(
        ...,
        description="Natural language description of the FPDEVSML model to generate",
        min_length=10,
        examples=["Create an M/M/1 queue model with arrival rate 5 and service rate 10"]
    )


class SubmitNLResponse(BaseModel):
    """Response model for natural language submission."""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(default="PENDING", description="Initial job status")
    message: str = Field(default="Job submitted successfully")


class JobStatus(BaseModel):
    """Job status response model."""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: Literal["PENDING", "PROCESSING", "SUCCESS", "FAILED"] = Field(
        ..., description="Current job status"
    )
    created_at: str = Field(..., description="Job creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class RetrievalContext(BaseModel):
    """Context retrieved from knowledge base."""

    source: str = Field(..., description="Source file or document")
    content: str = Field(..., description="Retrieved content")
    score: float = Field(..., description="Relevance score", ge=0.0, le=1.0)


class GenerationMetadata(BaseModel):
    """Metadata about the generation process."""

    retrieval_context: List[str] = Field(
        default_factory=list,
        description="List of sources used for context"
    )
    generation_time_ms: int = Field(..., description="Time taken to generate spec")
    model_type: Optional[str] = Field(None, description="Type of FPDEVSML model (atomic/coupled)")
    llm_provider: str = Field(..., description="LLM provider used")
    llm_model: str = Field(..., description="LLM model used")


class SpecResponse(BaseModel):
    """Response model for specification retrieval."""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: Literal["PENDING", "PROCESSING", "SUCCESS", "FAILED"] = Field(
        ..., description="Current job status"
    )
    fpdevsml_spec: Optional[str] = Field(
        None,
        description="Generated FPDEVSML specification (XML format)"
    )
    metadata: Optional[GenerationMetadata] = Field(
        None,
        description="Metadata about the generation process"
    )
    error: Optional[str] = Field(None, description="Error message if status is FAILED")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(default="healthy")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = Field(default="1.0.0")
