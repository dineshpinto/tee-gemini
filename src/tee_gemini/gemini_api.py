import logging

import google.generativeai as genai

from tee_gemini.gemini_endpoint import RequestResponse

logger = logging.getLogger(__name__)


class GeminiAPI:
    def __init__(self, model: str, api_key: str) -> None:
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        logger.info("Successfully connected to Gemini API with model `%s`", model)

    def make_query(self, uid: int, data: str) -> RequestResponse:
        res = self.model.generate_content(data)
        return RequestResponse(
            uid=uid,
            text=res.text,
            prompt_token_count=res.usage_metadata.prompt_token_count,
            candidates_token_count=res.usage_metadata.prompt_token_count,
            total_token_count=res.usage_metadata.total_token_count,
        )
