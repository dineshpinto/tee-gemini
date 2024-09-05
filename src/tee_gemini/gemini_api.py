import logging

import google.generativeai as genai

from tee_gemini.gemini_endpoint import GeminiResponse

logger = logging.getLogger(__name__)


class GeminiAPI:
    """Class to interface with the Google Gemini Generative AI API."""

    def __init__(self, model: str, api_key: str) -> None:
        """Initialize the Gemini API with a model and API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        logger.info("Successfully connected to Gemini API with model `%s`", model)

    async def make_query(self, uid: int, data: str) -> GeminiResponse:
        """Make an asynchronous query to the Gemini API and return a GeminiResponse."""
        res = await self.model.generate_content_async(data)

        # Check for the expected response attributes
        if not hasattr(res, "text") or not hasattr(res, "usage_metadata"):
            msg = f"Invalid response from Gemini API for UID {uid}"
            raise ValueError(msg)

        return GeminiResponse(
            uid=uid,
            text=res.text,
            prompt_token_count=res.usage_metadata.prompt_token_count,
            candidates_token_count=res.usage_metadata.prompt_token_count,
            total_token_count=res.usage_metadata.total_token_count,
        )
