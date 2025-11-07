"""Job storage management."""

import json
import aiosqlite
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)


class JobStorage:
    """Manages persistent storage of job data."""

    def __init__(self, db_path: Path = Path("./devagent/data/jobs/jobs.db")):
        """Initialize job storage."""
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """Initialize database schema."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    nl_query TEXT NOT NULL,
                    fpdevsml_spec TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.commit()
        logger.info("Database initialized", db_path=str(self.db_path))

    async def create_job(self, job_id: str, nl_query: str) -> None:
        """Create a new job."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO jobs (job_id, status, nl_query, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_id, "PENDING", nl_query, now, now)
            )
            await db.commit()
        logger.info("Job created", job_id=job_id)

    async def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        fpdevsml_spec: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update job status and data."""
        now = datetime.utcnow().isoformat()

        updates = ["updated_at = ?"]
        params = [now]

        if status:
            updates.append("status = ?")
            params.append(status)

        if fpdevsml_spec:
            updates.append("fpdevsml_spec = ?")
            params.append(fpdevsml_spec)

        if metadata:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

        params.append(job_id)

        query = f"UPDATE jobs SET {', '.join(updates)} WHERE job_id = ?"

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(query, params)
            await db.commit()

        logger.info("Job updated", job_id=job_id, status=status)

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job by ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM jobs WHERE job_id = ?",
                (job_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    job_dict = dict(row)
                    if job_dict.get("metadata"):
                        job_dict["metadata"] = json.loads(job_dict["metadata"])
                    return job_dict
                return None

    async def delete_job(self, job_id: str) -> None:
        """Delete a job."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
            await db.commit()
        logger.info("Job deleted", job_id=job_id)
