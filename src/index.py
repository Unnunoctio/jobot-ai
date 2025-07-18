from config import MIN_PUNTUATION
from job_spider.linkedin import LinkedIn
from latex_manager.latex_manager import LatexManager
from llm_model.llm_model import LLMModel
from resend_manager.resend_manager import ResendManager

jobs = LinkedIn().get_jobs()
jobs_rating = LLMModel().rate_jobs(jobs)

print([job.title for job in jobs])
print(jobs_rating)

for i in range(len(jobs_rating)):
    if jobs_rating[i] is None or jobs_rating[i] < MIN_PUNTUATION:
        continue

    job_objective = LLMModel().generate_objective_by_job(jobs[i])
    job_experiences = LLMModel().generate_experiences_by_job(jobs[i])

    LatexManager().write_objective(job_objective)
    LatexManager().write_experiences(job_experiences)
    LatexManager().compile()

    ResendManager().send_cv(jobs[i])

