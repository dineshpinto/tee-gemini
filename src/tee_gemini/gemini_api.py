import vertexai
from vertexai.generative_models import GenerativeModel

from tee_gemini.gemini_endpoint import RequestResponse

vertexai.init(project="flare-network-sandbox", location="europe-west1")


class GeminiAPI:
    def __init__(self) -> None:
        self.model = GenerativeModel("gemini-1.5-pro-001")

    def make_query(self, query: str) -> RequestResponse:
        res = self.model.generate_content(query)
        return RequestResponse(
            text=res.text,  # pyright: ignore [reportAttributeAccessIssue]
            prompt_token_count=res.usage_metadata.prompt_token_count,  # pyright: ignore [reportAttributeAccessIssue]
            candidates_token_count=res.usage_metadata.prompt_token_count,  # pyright: ignore [reportAttributeAccessIssue]
            total_token_count=res.usage_metadata.total_token_count,  # pyright: ignore [reportAttributeAccessIssue]
        )
