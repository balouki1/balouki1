#!/usr/bin/env python
"""Script to build the FAISS index from local documents."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from devagent.core.retriever import RetrieverAgent
from devagent.core.utils.config import get_settings
from devagent.core.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


def main():
    """Build FAISS index from FPDEVSML examples and documentation."""
    logger.info("Starting index build process")

    # Initialize retriever
    retriever = RetrieverAgent()

    # Load documents from both directories
    documents = []

    # Load FPDEVSML examples
    logger.info("Loading FPDEVSML examples", path=str(settings.fpdevsml_examples_path))
    examples = retriever.load_documents_from_directory(
        settings.fpdevsml_examples_path,
        file_extensions=['.xml']
    )
    documents.extend(examples)
    logger.info("Loaded FPDEVSML examples", count=len(examples))

    # Load documentation
    logger.info("Loading documentation", path=str(settings.documentation_path))
    docs = retriever.load_documents_from_directory(
        settings.documentation_path,
        file_extensions=['.md', '.txt']
    )
    documents.extend(docs)
    logger.info("Loaded documentation files", count=len(docs))

    # Build index
    if documents:
        logger.info("Building index", total_documents=len(documents))
        retriever.build_index(documents)
        logger.info(
            "Index built successfully",
            index_path=str(retriever.index_path),
            documents_path=str(retriever.documents_path)
        )
    else:
        logger.error("No documents found to index")
        sys.exit(1)


if __name__ == "__main__":
    main()
