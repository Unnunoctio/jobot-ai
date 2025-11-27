import os

import resend

# RESEND
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")


def handler(event, context):
    new_offers = event.get("new_offers", [])
    new_offers = [no for sublist in new_offers for no in sublist]

    resend.api_key = RESEND_API_KEY
    params: resend.Emails.SendParams = {
        "from": "Jobot AI <onboarding@resend.dev>",
        "to": EMAIL_SENDER,
        "subject": "Jobot AI - Ofertas de trabajo encontradas",
        "html": build_html(new_offers),
    }

    try:
        resend.Emails.send(params)
        return "OK"
    except Exception as e:
        raise Exception(f"Error to send email: {str(e)}")


def build_html(offers: list[dict]) -> str:
    html = "<h2>Ofertas de trabajo encontradas</h2><ul>"
    for o in offers:
        html += f"""
        <li>
            <strong>Título              :</strong> {o["title"]}<br>
            <strong>Ubicación           :</strong> {o["location"]}<br>
            <strong>Modalidad           :</strong> {o["modality"]}<br>
            <strong>Fecha Publicación   :</strong> {o["created_at"]}<br>
            <strong>N° de postulaciones :</strong> {o["applications"]}<br>
            <strong>Puntuación IA       :</strong> {o["score"]}<br>

            <strong>URL                 :</strong> <a href="{o["url"]}">{o["url"]}</a>
        </li>
        """
    html += "</ul><p>¡Gracias por utilizar Jobot AI!</p>"

    return html
