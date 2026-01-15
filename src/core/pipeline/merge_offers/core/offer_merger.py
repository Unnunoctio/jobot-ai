from typing import Dict, List, Set

from botocore.exceptions import ClientError
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table


class OfferMerger:
    """Handles merging, filtering, and batching of job offers."""

    BATCH_SIZE = 100  # DynamoDB batch_get_item limit
    OFFERS_PER_BATCH = 5  # Offers per scoring batch

    def __init__(self, client: DynamoDBClient, table: Table, table_name: str):
        self.client = client
        self.table = table
        self.table_name = table_name

    def process_offers(self, offers: List[List[Dict]]) -> Dict:
        """
        Pipeline:
        1. Flatten offer lists
        2. Filter already seen offers
        3. Batch remaining offers
        """

        flat_offers = self._flatten_offers(offers)
        if not flat_offers:
            print("No offers to process")
            return {
                "batches": None,
            }

        new_offers = self._filter_seen_offers(flat_offers)
        if not new_offers:
            print("No new offers to process")
            return {
                "batches": None,
            }

        batches = self._create_batches(new_offers)
        return {
            "batches": batches,
        }

    def _flatten_offers(self, offers: List[List[Dict]]) -> List[Dict]:
        """Flatten nested offer lists and validate structure."""

        flat_offers = []

        for offer_list in offers:
            if not isinstance(offer_list, list):
                print(f"Expected list but got {type(offer_list)}")
                continue

            for offer in offer_list:
                if self._is_valid_offer(offer):
                    flat_offers.append(offer)
                else:
                    print(f"Invalid offer structure: {offer}")

        return flat_offers

    def _is_valid_offer(self, offer: Dict) -> bool:
        """Validate that offer has required fields."""

        required_fields = ["url", "title", "company", "location", "modality", "created_at", "applications", "description", "spider"]
        return all(field in offer for field in required_fields)

    def _filter_seen_offers(self, offers: List[Dict]) -> List[Dict]:
        """Filter out offers that have already been processed."""

        offer_urls = [offer["url"] for offer in offers]
        seen_urls = self._get_seen_offer_urls(offer_urls)

        new_offers = [offer for offer in offers if offer["url"] not in seen_urls]
        return new_offers

    def _get_seen_offer_urls(self, urls: List[str]) -> Set[str]:
        """Query DynamoDB to check wich URLs have been seen."""

        seen_urls = set()

        for i in range(0, len(urls), self.BATCH_SIZE):
            chunk = urls[i : i + self.BATCH_SIZE]

            try:
                response = self.client.batch_get_item(
                    RequestItems={
                        self.table_name: {
                            "Keys": [{"url": {"S": url}} for url in chunk],
                        }
                    }
                )

                items = response.get("Responses", {}).get(self.table_name, [])
                for item in items:
                    seen_urls.add(item.get("url", {}).get("S"))

                unprocessed = response.get("UnprocessedKeys", {})
                if unprocessed:
                    print(f"{len(unprocessed)} unprocessed keys, may need retry logic")

            except ClientError as e:
                print(f"Error checking seen offers: {e}")
                continue

        return seen_urls

    def _create_batches(self, offers: List[Dict]) -> List[List[Dict]]:
        """Split offers into batches for parallel processing."""

        return [offers[i : i + self.BATCH_SIZE] for i in range(0, len(offers), self.BATCH_SIZE)]
