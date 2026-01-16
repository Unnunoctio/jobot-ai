import time
from typing import Any, Dict, List

from mypy_boto3_dynamodb.service_resource import Table
from prompts.prompt_manager import PromptManager
from providers._iprovider import IProvider


class OfferScorer:
    """Handles AI-powered scoring of job offers."""

    TTL_DAYS = 7

    def __init__(self, provider: IProvider, user_experience: str, min_score: int, table: Table):
        self.provider = provider
        self.user_experience = user_experience
        self.min_score = min_score
        self.table = table

    def process_batch(self, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of job offers.
        1. Score each offer with AI
        2. Save to DynamoDB
        3. Filter out offers with low scores
        """

        if not offers:
            return []

        scores = self._score_offers(offers)
        if not scores or len(scores) != len(offers):
            print(f"Expected {len(offers)} scores but got {len(scores)}")
            return []

        scored_offers = [{**offer, "score": score} for offer, score in zip(offers, scores)]

        self._save_offers(scored_offers)

        filtered_offers = self._filter_by_score(scored_offers)
        return filtered_offers

    def _score_offers(self, offers: List[Dict[str, Any]]) -> List[int]:
        """Use AI to score offers against user experience."""

        try:
            system_prompt = PromptManager.get_system_prompt()
            user_prompt = PromptManager.get_user_prompt(self.user_experience, offers)

            response = self.provider.generate(system=system_prompt, user=user_prompt, temp=1, top_p=0.9)

            scores = self._parse_scores(response, len(offers))
            return scores
        except Exception as e:
            print(f"Error scoring offers: {e}")
            return [50] * len(offers)

    def _parse_scores(self, response: str, expected_count: int) -> List[int]:
        """Parse comma-separated scores from AI response."""

        try:
            response = response.strip()

            score_strings = response.split(",")

            scores = [int(s.strip()) for s in score_strings]

            if len(scores) != expected_count:
                print(f"Expected {expected_count} scores, got {len(scores)}")
                if len(scores) < expected_count:
                    scores.extend([50] * (expected_count - len(scores)))
                else:
                    scores = scores[:expected_count]

            scores = [max(1, min(100, score)) for score in scores]
            return scores
        except Exception as e:
            print(f"Error parsing scores from AI response '{response}': {e}")
            return [50] * expected_count

    def _save_offers(self, offers: List[Dict[str, Any]]) -> None:
        """Save scored offers to DynamoDB with TTL."""

        ttl = int(time.time()) + (self.TTL_DAYS * 24 * 3600)

        try:
            with self.table.batch_writer() as batch:
                for offer in offers:
                    item = {
                        "url": offer["url"],
                        "ttl": ttl,
                        "title": offer["title"],
                        "company": offer["company"],
                        "created_at": offer["created_at"],
                        "score": offer["score"],
                    }
                    batch.put_item(Item=item)
        except Exception as e:
            print(f"Error saving offers to DynamoDB: {e}")

    def _filter_by_score(self, offers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out offers with low scores."""

        filtered_offers = [
            {
                "url": o["url"],
                "title": o["title"],
                "company": o["company"],
                "location": o["location"],
                "modality": o["modality"],
                "created_at": o["created_at"],
                "applications": o["applications"],
                "score": o["score"],
                "spider": o["spider"],
            }
            for o in offers
            if o["score"] >= self.min_score
        ]

        return filtered_offers
