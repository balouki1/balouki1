"""Orchestrator for coordinating RAG pipeline."""

import asyncio
from typing import Dict, Any
from .retriever import RetrieverAgent
from .nl2spec_agent import NL2SpecAgent
from .utils.storage import JobStorage
from .utils.logger import get_logger

logger = get_logger(__name__)


class Orchestrator:
    """Coordinates the RAG pipeline for FPDEVSML generation."""

    def __init__(
        self,
        retriever: RetrieverAgent,
        nl2spec_agent: NL2SpecAgent,
        storage: JobStorage
    ):
        """
        Initialize the orchestrator.

        Args:
            retriever: RetrieverAgent instance
            nl2spec_agent: NL2SpecAgent instance
            storage: JobStorage instance
        """
        self.retriever = retriever
        self.nl2spec_agent = nl2spec_agent
        self.storage = storage

        logger.info("Orchestrator initialized")

    async def process_request(
        self,
        job_id: str,
        nl_query: str
    ) -> Dict[str, Any]:
        """
        Process a natural language request through the RAG pipeline.

        Args:
            job_id: Unique job identifier
            nl_query: Natural language query

        Returns:
            Dictionary with job results
        """
        logger.info("Processing request", job_id=job_id, query=nl_query)

        try:
            # Update status to PROCESSING
            await self.storage.update_job(job_id, status="PROCESSING")

            # Step 1: Retrieve relevant context
            logger.info("Step 1: Retrieving context", job_id=job_id)
            context = await self.retriever.retrieve(nl_query)

            if not context:
                logger.warning("No context retrieved", job_id=job_id)
                await self.storage.update_job(
                    job_id,
                    status="FAILED",
                    metadata={
                        "error": "No relevant context found in knowledge base"
                    }
                )
                return {
                    "job_id": job_id,
                    "status": "FAILED",
                    "error": "No relevant context found in knowledge base"
                }

            # Step 2: Generate FPDEVSML specification
            logger.info("Step 2: Generating specification", job_id=job_id)
            generation_result = await self.nl2spec_agent.generate(nl_query, context)

            fpdevsml_spec = generation_result["spec"]
            metadata = generation_result["metadata"]

            # Step 3: Store results
            logger.info("Step 3: Storing results", job_id=job_id)
            await self.storage.update_job(
                job_id,
                status="SUCCESS",
                fpdevsml_spec=fpdevsml_spec,
                metadata=metadata
            )

            logger.info("Request processing completed", job_id=job_id)

            return {
                "job_id": job_id,
                "status": "SUCCESS",
                "fpdevsml_spec": fpdevsml_spec,
                "metadata": metadata
            }

        except Exception as e:
            logger.error("Request processing failed", job_id=job_id, error=str(e))

            # Update job status to FAILED
            await self.storage.update_job(
                job_id,
                status="FAILED",
                metadata={
                    "error": str(e)
                }
            )

            return {
                "job_id": job_id,
                "status": "FAILED",
                "error": str(e)
            }

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job.

        Args:
            job_id: Job identifier

        Returns:
            Job status information
        """
        job = await self.storage.get_job(job_id)

        if not job:
            logger.warning("Job not found", job_id=job_id)
            return None

        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"]
        }

    async def get_job_spec(self, job_id: str) -> Dict[str, Any]:
        """
        Get the full job results including specification.

        Args:
            job_id: Job identifier

        Returns:
            Complete job information
        """
        job = await self.storage.get_job(job_id)

        if not job:
            logger.warning("Job not found", job_id=job_id)
            return None

        result = {
            "job_id": job["job_id"],
            "status": job["status"],
            "fpdevsml_spec": job.get("fpdevsml_spec"),
            "metadata": job.get("metadata")
        }

        # Add error if status is FAILED
        if job["status"] == "FAILED" and job.get("metadata"):
            result["error"] = job["metadata"].get("error")

        return result
