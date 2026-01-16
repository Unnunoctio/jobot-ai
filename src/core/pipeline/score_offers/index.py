import os

import boto3
from core.offer_scorer import OfferScorer
from core.user_experience_loader import UserExperienceLoader
from providers.provider_manager import ProviderManager

# AWS Resources
dynamodb = boto3.resource("dynamodb")
seen_offers_table = dynamodb.Table(os.getenv("SEEN_OFFERS_TABLE") or "")

s3_client = boto3.client("s3")
s3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME") or ""

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER") or ""
AI_API_KEY = os.getenv("AI_API_KEY") or ""
AI_MODEL = os.getenv("AI_MODEL") or ""

# User Configuration
USER_EXPERIENCE_FILE = os.getenv("USER_EXPERIENCE_FILE") or ""
MIN_SCORE = int(os.getenv("MIN_SCORE") or "50")


def handler(event, context):
    """
    Lambda handler: Score a batch of job offers using AI.

    Input:
        event["batch"]: List of job offers to score

    Returns:
        List[Dict[str, Any]]: Filtered offers with score
    """

    try:
        batch = event.get("batch", [])
        if not batch:
            print("No offers to score")
            return []

        user_experience = UserExperienceLoader.load(s3_client, s3_BUCKET_NAME, USER_EXPERIENCE_FILE)

        provider = ProviderManager.get_ai_provider(AI_PROVIDER, AI_API_KEY, AI_MODEL)

        scorer = OfferScorer(provider, user_experience, MIN_SCORE, seen_offers_table)
        filtered_offers = scorer.process_batch(batch)

        return filtered_offers
    except Exception as e:
        print(f"Error in ScoreOffers handler: {e}")
        return []
