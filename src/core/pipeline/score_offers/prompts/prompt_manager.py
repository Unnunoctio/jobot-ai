from pathlib import Path
from typing import Any, Dict, List


class PromptManager:
    """Manages prompts for AI-powered scoring of job offers."""

    @staticmethod
    def get_system_prompt() -> str:
        """Load system prompt from file."""

        prompt_path = Path("prompts/system.txt")
        if not prompt_path.exists():
            raise FileNotFoundError(f"System prompt not found at {prompt_path}")

        return prompt_path.read_text(encoding="utf-8").strip()

    @staticmethod
    def get_user_prompt(user_experience: str, offers: List[Dict[str, Any]]) -> str:
        return f"""
        ---------------- USER EXPERIENCE ----------------
        {user_experience}

        ------------------- JOB OFFERS ------------------
        {chr(10).join([
            f"JOB OFFER #{i+1}\n"
            f"Title: {job['title']}\n"
            f"Location: {job['location']}\n"
            f"Modality: {job['modality']}\n"
            f"Description:\n{job['description']}\n"
            f"------------------------------------"
            for i, job in enumerate(offers)
        ])}
        """
