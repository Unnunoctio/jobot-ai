
def get_user_prompt(user_experience: str, job_offers: list[dict]) -> str:
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
    for i, job in enumerate(job_offers)
])}
"""    
