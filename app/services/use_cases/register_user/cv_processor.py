from fastapi import UploadFile
import logging
import re
import fitz
from typing import Dict, Any, Optional


from app.settings import settings
from app.services.prompts.prompts import SYSTEM_PROMPT, USER_PROMPT
from app.services.schemas.cv_info_schema import CVInfoSchema
from app.domain.ports.ia_service_port import IAService
from app.infrastructure.ai import ai_service
from app.services.exceptions.register_user_exceptions import (
    InvalidFileType,
    FileTooLarge,
    InvalidCV,
)
from app.infrastructure.ai.exceptions import ServiceLimitError, ParsingError

logger = logging.getLogger(__name__)


class CVProcessor:
    def __init__(
        self,
        ia_service: IAService = ai_service,
        system_prompt: str = SYSTEM_PROMPT,
        user_prompt: str = USER_PROMPT,
    ):
        self.ia_service = ia_service
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    async def process_cvs(
        self, personal_cv: UploadFile, linkedin_cv: UploadFile
    ) -> Dict[str, Any]:
        self._validate_pdf(personal_cv)
        self._validate_pdf(linkedin_cv)

        personal_cv_text = self._extract_text(personal_cv)
        linkedin_cv_text = self._extract_text(linkedin_cv, is_linkedin_cv=True)

        personal_cv_parsed = None
        if personal_cv_text:
            personal_cv_parsed = await self._parse_pdf_text(
                personal_cv_text, CVInfoSchema, self.system_prompt, self.user_prompt
            )
        else:
            personal_cv_parsed = await self._parse_pdf_file(personal_cv)

        linkedin_cv_parsed = None
        if linkedin_cv_text:
            logger.info(f"Parsed text: {linkedin_cv_text}")
            linkedin_cv_parsed = await self._parse_pdf_text(
                personal_cv_text, CVInfoSchema, self.system_prompt, self.user_prompt
            )
        else:
            raise InvalidCV("The provided LinkedIn CV file is corrupted")

        if not linkedin_cv_parsed:
            raise ParsingError("Failed to parse Linkedin CV, try agin")

        result = {
            "first_name": personal_cv_parsed.first_name,
            "last_name": personal_cv_parsed.last_name,
            "skills": list(set(personal_cv_parsed.skills + linkedin_cv_parsed.skills)),
            "english_level": personal_cv_parsed.english_level,
            "linkedin_url": linkedin_cv_parsed.linkedin_url,
            "works_in_it": personal_cv_parsed.works_in_it,
        }

        return result

    def _validate_pdf(self, file: UploadFile):
        """Validate that the file is a PDF and does not exceed the size limit."""
        MAX_PDF_SIZE_BYTES = settings.max_pdf_size * 1024 * 1024

        if not file.content_type.startswith("application/pdf"):
            raise InvalidFileType(f"{file.filename} is not a valid PDF file")

        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        if size > MAX_PDF_SIZE_BYTES:
            raise FileTooLarge(
                f"{file.filename} exceeds {settings.max_pdf_size:.1f}MB limit"
            )

    def _extract_text(
        self, file: UploadFile, is_linkedin_cv: bool = False
    ) -> Optional[str]:
        try:
            contents = file.file.read()
            with fitz.open(stream=contents, filetype="pdf") as doc:
                # More exhaustive check using fitz metadata to verify LinkedIn CV
                if is_linkedin_cv:
                    metadata = doc.metadata or {}
                    creator = (metadata.get("author") or "").lower()
                    producer = (metadata.get("producer") or "").lower()
                    if not any("linkedin" in field for field in (creator, producer)):
                        raise InvalidCV(
                            f"{file.filename} metadata no indica que sea de LinkedIn"
                        )

                # Extract text from up to the first 2 pages
                pages_text = [page.get_text() for page in doc[:2]]
                full_text = "\n\n".join(pages_text)

                # Clean text, less lines, less tokens consumed.
                full_text = re.sub(r"\n{3,}", "\n\n", full_text).strip()

                # Validate if extracted text is usefull
                if len(full_text) < 50:
                    raise ValueError

                return full_text
        except fitz.FileDataError:
            raise InvalidFileType(f"{file.filename} is not a valid PDF file")
        except InvalidCV:
            raise
        except Exception:
            return None
        finally:
            file.file.seek(0)

    async def _parse_pdf_text(
        self, cv_text: str, schema: CVInfoSchema, system_prompt: str, user_prompt: str
    ):
        parsed_cv = None
        try:
            parsed_cv = await ai_service.parse_text_with_schema(
                cv_text, schema, system_prompt, user_prompt
            )
        except ParsingError as e:
            logger.critical(f"Failed to parse cv: {e}")
        return parsed_cv

    async def _parse_pdf_file(
        self,
        file: UploadFile,
        schema: CVInfoSchema,
        system_prompt: str,
        user_prompt: str,
    ):
        content = file.file.read()
        parsed_cv = await ai_service.parse_pdf_with_schema(
            content, schema, system_prompt, user_prompt
        )
        file.file.seek(0)
        return parsed_cv
