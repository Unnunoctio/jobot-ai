from openai import OpenAI
from providers._iprovider import IProvider


class OpenAIProvider(IProvider):
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, system: str, user: str, temp: float = 0, top_p: float = 1) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=temp,
                top_p=top_p,
            )

            if not response.choices:
                raise Exception("No response from OpenAI API")

            content = response.choices[0].message.content

            if content is None:
                raise Exception("No content from OpenAI API")
            if not content.strip():
                raise Exception("Empty content from OpenAI API")

            return content.strip()
        except Exception as e:
            raise Exception(f"Error from OpenAI API: {str(e)}")
