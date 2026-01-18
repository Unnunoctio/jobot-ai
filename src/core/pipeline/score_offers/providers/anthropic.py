import anthropic
from providers._iprovider import IProvider


class Anthropic(IProvider):
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, system: str, user: str, temp: float = 0, top_p: float = 1) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=temp,
                top_p=top_p,
                system=system,
                messages=[
                    {"role": "user", "content": user},
                ],
            )

            if not response.content:
                raise Exception("No content from Anthropic API")

            content = response.content[0].text  # type: ignore

            if content is None:
                raise Exception("No content from Anthropic API")
            if not content.strip():
                raise Exception("Empty content from Anthropic API")

            return content.strip()
        except Exception as e:
            raise Exception(f"Error from Anthropic API: {str(e)}")
