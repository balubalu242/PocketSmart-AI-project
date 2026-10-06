import base64
import json
import logging
from typing import Any

from pydantic import ValidationError

from app.config import get_settings
from app.models.schemas import RecommendationResponse

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        if self.settings.gemini_api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.settings.gemini_api_key)
            except Exception:
                logger.exception("Unable to initialize Gemini client")

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def generate(
        self,
        prompt: str,
        image_bytes: bytes | None = None,
        image_mime: str | None = None,
    ) -> RecommendationResponse | None:
        if not self.client:
            return None

        try:
            from google.genai import types

            contents: list[Any] = [prompt]
            if image_bytes:
                contents.append(
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=image_mime or "image/jpeg",
                    )
                )

            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RecommendationResponse,
                    temperature=0.4,
                ),
            )

            if getattr(response, "parsed", None):
                parsed = response.parsed
                if isinstance(parsed, RecommendationResponse):
                    return parsed
                return RecommendationResponse.model_validate(parsed)

            text = getattr(response, "text", None)
            if not text:
                return None

            data = json.loads(text)
            return RecommendationResponse.model_validate(data)

        except (ValidationError, ValueError, json.JSONDecodeError):
            logger.exception("Gemini returned an invalid structured response")
            return None
        except Exception:
            logger.exception("Gemini request failed")
            return None


def image_to_data_uri(image_bytes: bytes, mime: str) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{encoded}"
