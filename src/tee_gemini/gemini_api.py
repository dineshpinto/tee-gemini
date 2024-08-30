import logging

import vertexai
from vertexai.generative_models import GenerativeModel

from tee_gemini.gemini_endpoint import RequestResponse

logger = logging.getLogger(__name__)

vertexai.init(project="flare-network-sandbox", location="europe-west1")


class GeminiAPI:
    def __init__(self, model: str) -> None:
        self.model = GenerativeModel(model)
        logger.info("Successfully connected to VertexAI API with model `%s`", model)

    def make_query(self, uid: int, data: str) -> RequestResponse:
        res = self.model.generate_content(data)
        return RequestResponse(
            uid=uid,
            text=res.text,  # pyright: ignore [reportAttributeAccessIssue]
            prompt_token_count=res.usage_metadata.prompt_token_count,  # pyright: ignore [reportAttributeAccessIssue]
            candidates_token_count=res.usage_metadata.prompt_token_count,  # pyright: ignore [reportAttributeAccessIssue]
            total_token_count=res.usage_metadata.total_token_count,  # pyright: ignore [reportAttributeAccessIssue]
        )
