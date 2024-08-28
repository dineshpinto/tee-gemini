import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="flare-network-sandbox", location="europe-west1")


class GeminiAPI:
    def __init__(self) -> None:
        self.model = GenerativeModel("gemini-1.5-pro-001")

    def make_query(self, query: str) -> str:
        return self.model.generate_content(query).text
