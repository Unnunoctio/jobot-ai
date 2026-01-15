from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


@dataclass
class SpiderConfig:
    """Spider configuration model"""

    id: str
    enabled: bool
    lambda_name: str
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Validate required config fields
        if "keywords" not in self.config:
            self.config["keywords"] = []
        if "params" not in self.config:
            self.config["params"] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize SpiderConfig to dictionary for JSON responses."""

        return {
            "id": self.id,
            "enabled": self.enabled,
            "lambda_name": self.lambda_name,
            "config": self.config,
        }


@dataclass
class Offer:
    """Offer model"""

    url: str
    title: str
    company: str
    location: str
    modality: str
    created_at: datetime
    applications: str
    description: str
    spider: str

    def __post_init__(self):
        pass
