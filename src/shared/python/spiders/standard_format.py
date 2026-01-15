def create_standard_offer(
    url: str,
    title: str,
    company: str,
    location: str,
    modality: str,
    created_at: str,
    description: str,
    applications: str,
    spider: str,
) -> dict:
    """Factory method to create a standard format for a job offer"""
    return {
        "url": url,
        "title": title,
        "company": company,
        "location": location,
        "modality": modality,
        "created_at": created_at,
        "description": description,
        "applications": applications,
        "spider": spider,
    }
