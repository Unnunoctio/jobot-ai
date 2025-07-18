import base64

import resend

from config import EMAIL_SENT, RESEND_API_KEY


class ResendManager:
    def __init__(self):
        pass

    def send_cv(self, job):
        resend.api_key = RESEND_API_KEY

        with open("output/main.pdf", "rb") as f:
            file_content = f.read()
            pdf_base64 = base64.b64encode(file_content).decode("utf-8")

        params: resend.Emails.SendParams = {
            "from": "Jobot AI <onboarding@resend.dev>",
            "to": [EMAIL_SENT],
            "subject": "Jobot AI - Oferta de trabajo encontrada",
            "html": f"""
                <h2>Oferta de trabajo encontrada</h2>
                <p>Hola, parece que hay una oferta de trabajo que se ajusta a tus habilidades y experiencia.</p>

                <strong>Titulo:         </strong>{job.title}<br>
                <strong>Compañía:       </strong>{job.company}<br>
                <strong>Localización:   </strong>{job.location}<br>
                <strong>Modalidad:      </strong>{job.modality}<br>
                <strong>Postulaciones:  </strong>{job.requests}<br>

                <strong>URL:            </strong><a href="{job.url}">{job.url}</a>

                <p>Se adjunta el CV personalizado para la oferta de trabajo.</p>
                <p>¡Gracias por utilizar Jobot AI!</p>
            """,
            "attachments": [
                {
                    "filename": "cv.pdf",
                    "content": pdf_base64,
                    "content_type": "application/pdf",
                }
            ]
        }
        try:
            resend.Emails.send(params)
        except Exception as e:
            print(f"Error al enviar el CV: {e}")
