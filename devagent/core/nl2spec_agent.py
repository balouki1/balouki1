"""NL2Spec Agent for generating FPDEVSML specifications from natural language."""

import re
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from .utils.logger import get_logger
from .utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class NL2SpecAgent:
    """Generates FPDEVSML specifications from natural language using LLM."""

    PROMPT_TEMPLATE = """You are an expert in FPDEVSML (Formal Parallel DEVS Modeling Language).
Your task is to generate a valid FPDEVSML specification based on the user's natural language description.

User Query:
{nl_query}

Relevant Context (Examples and Documentation):
{context}

Instructions:
1. Analyze the user query to understand the required model type (atomic or coupled)
2. Use the provided context as reference for syntax and structure
3. Generate ONLY the FPDEVSML XML specification
4. Ensure all required elements are present and properly structured
5. Do NOT include any explanations, comments, or text outside the XML

Generate the FPDEVSML specification now:"""

    def __init__(
        self,
        llm_provider: str = None,
        llm_model: str = None,
        openai_api_key: str = None,
        anthropic_api_key: str = None
    ):
        """
        Initialize the NL2Spec agent.

        Args:
            llm_provider: LLM provider ('openai' or 'anthropic')
            llm_model: Model name to use
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
        """
        self.llm_provider = llm_provider or settings.llm_provider
        self.llm_model = llm_model or settings.llm_model

        logger.info(
            "Initializing NL2SpecAgent",
            provider=self.llm_provider,
            model=self.llm_model
        )

        # Initialize LLM client
        if self.llm_provider == "openai":
            api_key = openai_api_key or settings.openai_api_key
            if not api_key:
                raise ValueError("OpenAI API key is required")
            self.client = AsyncOpenAI(api_key=api_key)
        elif self.llm_provider == "anthropic":
            api_key = anthropic_api_key or settings.anthropic_api_key
            if not api_key:
                raise ValueError("Anthropic API key is required")
            self.client = AsyncAnthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

        logger.info("LLM client initialized", provider=self.llm_provider)

    def _build_prompt(
        self,
        nl_query: str,
        context: List[Dict[str, Any]]
    ) -> str:
        """
        Build the prompt for LLM generation.

        Args:
            nl_query: Natural language query
            context: List of retrieved context documents

        Returns:
            Formatted prompt string
        """
        # Format context
        context_str = ""
        for i, ctx in enumerate(context, 1):
            context_str += f"\n--- Example {i} (from {ctx['source']}) ---\n"
            context_str += ctx['content'][:1000]  # Limit length
            context_str += "\n"

        # Build full prompt
        prompt = self.PROMPT_TEMPLATE.format(
            nl_query=nl_query,
            context=context_str
        )

        return prompt

    async def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API.

        Args:
            prompt: Formatted prompt

        Returns:
            LLM response
        """
        logger.info("Calling OpenAI API", model=self.llm_model)

        response = await self.client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in FPDEVSML. Generate only valid XML specifications."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )

        content = response.choices[0].message.content
        logger.info("OpenAI response received", length=len(content))
        return content

    async def _call_anthropic(self, prompt: str) -> str:
        """
        Call Anthropic API.

        Args:
            prompt: Formatted prompt

        Returns:
            LLM response
        """
        logger.info("Calling Anthropic API", model=self.llm_model)

        response = await self.client.messages.create(
            model=self.llm_model,
            max_tokens=2000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.content[0].text
        logger.info("Anthropic response received", length=len(content))
        return content

    def _extract_xml(self, response: str) -> str:
        """
        Extract XML from LLM response.

        Args:
            response: Raw LLM response

        Returns:
            Extracted XML string
        """
        # Try to extract XML between <?xml and closing tag
        xml_pattern = r'(<\?xml.*?</[^>]+>)'
        matches = re.findall(xml_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no <?xml tag, try to find just the model tags
        model_pattern = r'(<model.*?</model>)'
        matches = re.findall(model_pattern, response, re.DOTALL | re.IGNORECASE)

        if matches:
            # Add XML declaration
            return f'<?xml version="1.0" encoding="UTF-8"?>\n{matches[0].strip()}'

        # Return as-is if no XML found (might still be valid)
        logger.warning("Could not extract XML from response, returning raw content")
        return response.strip()

    def _detect_model_type(self, spec: str) -> Optional[str]:
        """
        Detect the type of FPDEVSML model.

        Args:
            spec: FPDEVSML specification

        Returns:
            'atomic', 'coupled', or None
        """
        if '<atomic' in spec.lower():
            return 'atomic'
        elif '<coupled' in spec.lower():
            return 'coupled'
        return None

    async def generate(
        self,
        nl_query: str,
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate FPDEVSML specification from natural language.

        Args:
            nl_query: Natural language query
            context: Retrieved context documents

        Returns:
            Dictionary with 'spec' and 'metadata' keys
        """
        import time

        logger.info("Generating FPDEVSML specification", query=nl_query)
        start_time = time.time()

        # Build prompt
        prompt = self._build_prompt(nl_query, context)

        # Call LLM
        try:
            if self.llm_provider == "openai":
                response = await self._call_openai(prompt)
            elif self.llm_provider == "anthropic":
                response = await self._call_anthropic(prompt)
            else:
                raise ValueError(f"Unsupported provider: {self.llm_provider}")
        except Exception as e:
            logger.error("LLM call failed", error=str(e))
            raise

        # Extract XML
        spec = self._extract_xml(response)

        # Calculate generation time
        generation_time_ms = int((time.time() - start_time) * 1000)

        # Detect model type
        model_type = self._detect_model_type(spec)

        # Prepare metadata
        metadata = {
            "retrieval_context": [ctx["source"] for ctx in context],
            "generation_time_ms": generation_time_ms,
            "model_type": model_type,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model
        }

        logger.info(
            "Specification generated",
            model_type=model_type,
            generation_time_ms=generation_time_ms,
            spec_length=len(spec)
        )

        return {
            "spec": spec,
            "metadata": metadata
        }
