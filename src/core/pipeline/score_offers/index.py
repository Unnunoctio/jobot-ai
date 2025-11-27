import os
from pathlib import Path

import boto3
from prompts.user import get_user_prompt
from providers._iprovider import IProvider

# AWS
DYNAMODB = boto3.resource("dynamodb")
SEEN_OFFERS_TABLE = DYNAMODB.Table(os.getenv("SEEN_OFFERS_TABLE"))

S3_CLIENT = boto3.client("s3")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# AI
AI_PROVIDER = os.getenv("AI_PROVIDER")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

# USER
USER_EXPERIENCE_FILE = os.getenv("USER_EXPERIENCE_FILE")
MIN_SCORE = int(os.getenv("MIN_SCORE"))


def handler(event, context):
    # TODO: Obtener el batch de ofertas
    offers = event.get("batch", [])

    # TODO: Obtener el user experience desde S3
    response = S3_CLIENT.get_object(Bucket=S3_BUCKET_NAME, Key=USER_EXPERIENCE_FILE)
    user_experience = response["Body"].read().decode("utf-8")

    # TODO: Obtener el score de cada oferta
    offer_scores = rate_offers(offers, user_experience)

    # TODO: Actualizar cada oferta con su score
    updated_offers = []
    for offer, score in zip(offers, offer_scores):
        offer["score"] = score
        updated_offers.append(offer)

    # TODO: Guardar las ofertas vistas
    with SEEN_OFFERS_TABLE.batch_writer() as batch:
        for offer in updated_offers:
            item = {
                "url": offer["url"],
                "title": offer["title"],
                "created_at": offer["created_at"],
                "score": offer["score"],
            }
            batch.put_item(Item=item)

    # TODO: Filtrar las ofertas con score mayor a "x"
    filtered_offers = [
        {
            "url": o["url"],
            "title": o["title"],
            "location": o["location"],
            "modality": o["modality"],
            "created_at": o["created_at"],
            "applications": o["applications"],
            "score": o["score"],
        }
        for o in updated_offers
        if o["score"] >= MIN_SCORE
    ]

    # TODO: Retornar las ofertas filtradas
    return filtered_offers


def rate_offers(offers: list[dict], user_experience: str) -> list[int]:
    try:
        ai_model = _get_provider()

        path = Path("prompts/system.txt")
        if not path.exists():
            raise FileNotFoundError("System prompt not found")

        system_prompt = path.read_text(encoding="utf-8").strip()
        user_prompt = get_user_prompt(user_experience, offers)

        rates_string = ai_model.generate(system_prompt, user_prompt, temp=1, top_p=0.9)
        rates_split = rates_string.split(",")

        return [int(rate.strip()) for rate in rates_split]
    except ValueError as e:
        print(e)
        return []


def _get_provider() -> IProvider:
    if AI_PROVIDER == "OPENAI":
        from providers.openai import OpenAIProvider

        return OpenAIProvider(AI_API_KEY, AI_MODEL)
    elif AI_PROVIDER == "DEEPSEEK":
        from providers.deepseek import DeepSeekProvider

        return DeepSeekProvider(AI_API_KEY, AI_MODEL)
    # TODO: Add Others
    else:
        raise ValueError(f"Provider {AI_PROVIDER} not supported")
