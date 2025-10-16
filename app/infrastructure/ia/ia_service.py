from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage, ModelRequest, UserPromptPart


class AIService:
    """
    Servicio genérico para parsear texto o archivos PDF usando IA
    con schemas de Pydantic.
    """

    def __init__(self, model: str = "openai:gpt-4o-mini"):
        """
        Inicializa el servicio de IA.

        Args:
            model: Modelo a usar. Ejemplos:
                - "openai:gpt-4o-mini" (gratis con créditos iniciales)
                - "gemini-1.5-flash" (gratis)
                - "anthropic:claude-sonnet-4-5" (pago)
        """
        self.agent = Agent(model)

    async def parse_text_with_schema(
        self, text: str, schema: type[BaseModel], system_prompt: str | None = None
    ) -> dict:
        if not text or not text.strip():
            raise ValueError("No text provided for parsing")

        agent = Agent(self.agent.model, result_type=schema, system_prompt=system_prompt)

        result = await agent.run(text)
        return result.data.model_dump()

    async def parse_pdf_with_schema(
        self,
        pdf_bytes: bytes,
        schema: type[BaseModel],
        system_prompt: str | None = None,
    ) -> dict:
        if not pdf_bytes:
            raise ValueError("No file provided for parsing")

        agent = Agent(self.agent.model, result_type=schema, system_prompt=system_prompt)

        message = ModelRequest(
            parts=[
                UserPromptPart(
                    content="Analiza este documento y extrae la información estructurada",
                    part_kind="user-prompt",
                ),
                UserPromptPart(content=pdf_bytes, part_kind="user-prompt"),
            ]
        )

        result = await agent.run(message)
        return result.data.model_dump()
