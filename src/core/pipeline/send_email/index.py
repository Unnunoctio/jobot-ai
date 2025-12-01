import os

import resend

# RESEND
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")


def handler(event, context):
    new_offers = event.get("new_offers", [])
    new_offers = [no for sublist in new_offers for no in sublist]

    if not new_offers or len(new_offers) == 0:
        return "No offers to send"

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
    html = """
    <div style="font-family: Arial, sans-serif; color: #222; max-width: 600px; margin: auto;">
        <h2 style="text-align: center; color: #2b6cb0;">Ofertas de trabajo encontradas</h2>
        <p style="color: #444; text-align: center;">
            Estas son las oportunidades que coinciden con tu perfil 👇
        </p>
        <ul style="list-style: none; padding: 0;">
    """

    for o in offers:
        html += f"""
            <li style="
                background: #f9fafb;
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
                border-left: 5px solid #2b6cb0;
            ">
                <h3 style="margin: 0 0 8px 0; color: #2b6cb0;">{o["title"]}</h3>

                <p style="margin: 4px 0;"><strong>Ubicación:</strong> {o["location"]}</p>
                <p style="margin: 4px 0;"><strong>Modalidad:</strong> {o["modality"]}</p>
                <p style="margin: 4px 0;"><strong>Fecha Publicación:</strong> {o["created_at"]}</p>
                <p style="margin: 4px 0;"><strong>N° de Postulaciones:</strong> {o["applications"]}</p>
                <p style="margin: 4px 0;"><strong>Puntuación IA:</strong> {o["score"]}</p>

                <p style="margin-top: 10px;">
                    <a href="{o["url"]}" style="
                        background: #2b6cb0;
                        color: #fff;
                        padding: 10px 14px;
                        text-decoration: none;
                        border-radius: 6px;
                        display: inline-block;
                    ">
                        Ver oferta
                    </a>
                </p>
            </li>
        """

    html += """
        </ul>
        <p style="margin-top: 20px; text-align: center; color: #555;">
            ¡Gracias por utilizar <strong>Jobot AI</strong>! 🚀
        </p>
    </div>
    """

    return html

