import asyncio
import logging
from pydantic import BaseModel, ValidationError
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider

from app.settings import settings
from app.infrastructure.ai.exceptions import ParsingError, ServiceLimitError

logger = logging.getLogger(__name__)


class AIService:
    """
    Generic AI service for parsing text or PDF files using Pydantic schemas.

    This service supports multiple AI providers and models, including Google Gemini,
    OpenAI GPT, and Anthropic Claude. It can handle retries for temporary service
    errors or parsing/validation failures.
    """

    def __init__(
        self,
        model=None,
        api_key: str = settings.gemini_api_key,
        provider=None,
        attempts: int = 2,
    ):
        """
        Initialize the AI service.

        Args:
            model (optional): The AI model to use. Examples:
                - "openai:gpt-4o-mini" (free with initial credits)
                - "gemini-2.0-flash" (free)
                - "anthropic:claude-sonnet-4-5" (paid)
            api_key (str, optional): API key for the AI provider.
            provider (optional): AI provider instance. Defaults to GoogleProvider.
            attempts (int, optional): Number of retry attempts on failure. Default is 2.
        """
        self.api_key = api_key
        self.provider = provider or GoogleProvider(api_key=self.api_key)
        self.model = model or GoogleModel("gemini-2.0-flash", provider=self.provider)
        self.attempts = attempts

    async def parse_text_with_schema(
        self,
        text: str,
        schema: type[BaseModel],
        system_prompt: str,
        user_prompt: str,
    ):
        """
        Parse plain text using the specified Pydantic schema.

        Args:
            text (str): The text content to parse.
            schema (type[BaseModel]): Pydantic schema class to validate and parse the response.
            system_prompt (str): Prompt that sets up the AI system behavior.
            user_prompt (str): User-specific prompt to guide the AI's parsing.

        Returns:
            BaseModel: Instance of the schema with parsed content.

        Raises:
            ValueError: If text is empty or None.
            ServiceLimitError: If the AI service rate limit or internal error occurs.
            ParsingError: If parsing fails or validation does not pass.
        """
        if not text or not text.strip():
            raise ValueError("No text provided for parsing")

        for attempt in range(self.attempts):
            try:
                agent = Agent(
                    self.model,
                    model_settings=GoogleModelSettings(
                        google_thinking_config={"include_thoughts": True}
                    ),
                    output_type=schema,
                    system_prompt=system_prompt,
                )
                result = await agent.run([user_prompt, text])
                return result.output

            except (ValidationError, Exception) as e:
                error_msg = str(e).lower()

                # Limit or service errors.
                if any(
                    term in error_msg
                    for term in [
                        "rate limit",
                        "429",
                        "500",
                        "503",
                        "502",
                        "quota",
                        "limit exceeded",
                    ]
                ):
                    if attempt == 0:
                        logger.warning(
                            f"Service limit/error on attempt {attempt + 1}, retrying..."
                        )
                        await asyncio.sleep(2)
                        continue
                    raise ServiceLimitError(
                        "Limit reached, or internal error, please try again later"
                    ) from e

                # Error parsing/validation
                if (
                    isinstance(e, ValidationError)
                    or "parse" in error_msg
                    or "validation" in error_msg
                ):
                    if attempt == 0:
                        logger.warning(
                            f"Parsing error on attempt {attempt + 1}, retrying..."
                        )
                        await asyncio.sleep(1)
                        continue
                    raise ParsingError(
                        "The provided CV cannot be processed. Please provide valid content."
                    ) from e

                # Other errors
                if attempt == 0:
                    logger.warning(f"Error on attempt {attempt + 1}: {e}, retrying...")
                    await asyncio.sleep(5)
                    continue

                # Throw generic error if all attempts fail
                raise ParsingError(f"Failed to parse text: {str(e)}") from e

    async def parse_pdf_with_schema(
        self,
        pdf_bytes: bytes,
        schema: type[BaseModel],
        system_prompt: str,
        user_prompt: str,
    ):
        """
        Parse PDF content using the specified Pydantic schema.

        Args:
            pdf_bytes (bytes): Raw PDF file bytes to parse.
            schema (type[BaseModel]): Pydantic schema class to validate and parse the response.
            system_prompt (str): Prompt that sets up the AI system behavior.
            user_prompt (str): User-specific prompt to guide the AI's parsing.

        Returns:
            BaseModel: Instance of the schema with parsed content.

        Raises:
            ValueError: If PDF bytes are empty.
            ServiceLimitError: If the AI service rate limit or internal error occurs.
            ParsingError: If parsing fails or validation does not pass.
        """
        if not pdf_bytes:
            raise ValueError("No file provided for parsing")

        for attempt in range(self.attempts):
            try:
                agent = Agent(
                    self.model, output_type=schema, system_prompt=system_prompt
                )
                result = await agent.run(
                    [
                        user_prompt,
                        BinaryContent(data=pdf_bytes, media_type="application/pdf"),
                    ]
                )
                return result.output

            except (ValidationError, Exception) as e:
                error_msg = str(e).lower()

                if any(
                    term in error_msg
                    for term in [
                        "rate limit",
                        "429",
                        "500",
                        "503",
                        "502",
                        "quota",
                        "limit exceeded",
                    ]
                ):
                    if attempt == 0:
                        logger.warning(
                            f"Service limit/error on attempt {attempt + 1}, retrying..."
                        )
                        await asyncio.sleep(2)
                        continue
                    raise ServiceLimitError(
                        "Limit reached, or internal error, please try again later"
                    ) from e

                if isinstance(e, ValidationError) or any(
                    term in error_msg
                    for term in [
                        "parse",
                        "validation",
                        "image",
                        "render",
                        "corrupt",
                        "invalid pdf",
                    ]
                ):
                    if attempt == 0:
                        logger.warning(
                            f"PDF parsing error on attempt {attempt + 1}, retrying..."
                        )
                        await asyncio.sleep(1)
                        continue
                    raise ParsingError(
                        "The provided PDF cannot be processed. Please enter a template other than a converted image or one with unrendered text."
                    ) from e

                if attempt == 0:
                    logger.warning(f"Error on attempt {attempt + 1}: {e}, retrying...")
                    await asyncio.sleep(1)
                    continue

                raise ParsingError(f"Failed to parse PDF: {str(e)}") from e
