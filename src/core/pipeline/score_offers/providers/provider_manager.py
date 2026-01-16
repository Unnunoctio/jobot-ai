from providers._iprovider import IProvider


class ProviderManager:
    """Manages AI providers."""

    @staticmethod
    def get_ai_provider(provider_name: str, api_key: str, model: str) -> IProvider:
        """Factory method to get configured AI provider."""

        if provider_name == "OPENAI":
            from providers.openai import OpenAIProvider

            return OpenAIProvider(api_key, model)
        elif provider_name == "DEEPSEEK":
            from providers.deepseek import DeepSeekProvider

            return DeepSeekProvider(api_key, model)
        # TODO: Add Others
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")
