from openai import OpenAI

from config import DEEPSEEK_API_KEY, USER_EXPERIENCE


class LLMModel:
    def __init__(self):
        self.model = "deepseek-chat"
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

    def rate_jobs(self, jobs):
        system_message = """
            You are a job offer scorer, where your task is to evaluate whether job offers align with the user's experience.
            - You must evaluate each job offer against the user's experience.
            - You must respond with a number between 1 and 100, with 1 being the lowest and 100 being the highest.
            - You must respond with only the number, do not include any explanation.
            - Scores must be exact and must not include decimals.
            - Each score must be separated by a comma and must follow the same order as the job offers (to identify them correctly).
        """
        user_message = f"""
            ---------------- USER EXPERIENCE ----------------
            {USER_EXPERIENCE}
            ---------------- JOB OFFERS ---------------------
            {[f"\n{job.data()}\n------------------------------------" for job in jobs]}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=1,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No se pudo obtener la respuesta del modelo.")

            return [int(score.strip()) for score in content.split(",")]
        except Exception as e:
            print(f"Error al evaluar las ofertas de trabajos: {e}")
            return None

    def generate_objective_by_job(self, job):
        system_message = """
            Your task is to evaluate the job offer and generate a professional objective that aligns with the user's experience, the user's own objective, and the job offer.
            - The objective must be written in Spanish.
            - The objective must not include any reference to the job offer.
            - The objective must not include any reference to the user's experience.
            - You must respond only with the objective, do not include any explanation.
        """
        user_message = f"""
            ---------------- USER EXPERIENCE ----------------
            {USER_EXPERIENCE}
            ---------------- JOB OFFER ----------------------
            {job.data()}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=1.5,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No se pudo obtener la respuesta del modelo.")

            return content.strip()
        except Exception as e:
            print(f"Error al evaluar las ofertas de trabajos: {e}")
            return None

    def generate_experiences_by_job(self, job):
        system_message = """
            Your task is to evaluate the job offer and generate a list of the user's professional experiences, adapting the tasks performed in each role to match the job offer's profile, without altering the original essence of each experience.
            Instructions:
            - Generate a list of the user's professional experiences.
            - Each experience must include 2 to 4 tasks, aligned with the focus of the job offer.
            - The tasks must be written in Spanish.
            - Do not include any direct references to the job offer.
            - Experiences must be ordered from most recent to oldest.
            - Each experience should be separated by a new line.
            - Use the following format for each experience: <company>#<position>#<period>#<task1|task2|...>
                Make sure each section is properly separated with a # symbol.
                Each task must end with a period (.).
                The <period> must abbreviate the month names to 3 letters (e.g., Enero -> Ene, Febrero -> Feb, etc.).
            IMPORTANT: Adapt the tasks to align with the requirements of the job offer to ensure relevance, but preserve the original meaning of each experience.
        """
        user_message = f"""
            ---------------- USER EXPERIENCE ----------------
            {USER_EXPERIENCE}
            ---------------- JOB OFFER ----------------------
            {job.data()}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=1,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No se pudo obtener la respuesta del modelo.")

            return [line.strip().split("#") for line in content.split("\n") if line.strip()]
        except Exception as e:
            print(f"Error al evaluar las ofertas de trabajos: {e}")
            return None
