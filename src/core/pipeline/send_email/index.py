import os

from core.email_builder import EmailBuilder
from core.email_sender import EmailSender

# RESEND
RESEND_API_KEY = os.getenv("RESEND_API_KEY") or ""
EMAIL_SENDER = os.getenv("EMAIL_SENDER") or ""


def handler(event, context):
    """
    Lambda handler: Send email with with job offers.

    Input:
        event["new_offers"]: List of lists of filtered offers

    Returns:
        str: Status message
    """

    try:
        new_offers = event.get("new_offers", [])
        flat_offers = [offer for sublist in new_offers for offer in (sublist if isinstance(sublist, list) else [sublist])]

        if not flat_offers or len(flat_offers) == 0:
            return "No offers to send"

        html = EmailBuilder.build_html(sorted(flat_offers, key=lambda o: o["score"], reverse=True))

        if len(flat_offers) == 1:
            subject = "Jobot AI - 1 nueva oferta de trabajo"
        else:
            subject = f"Jobot AI - {len(flat_offers)} nuevas ofertas de trabajo"

        sender = EmailSender(RESEND_API_KEY)
        success = sender.send(to=EMAIL_SENDER, subject=subject, html=html)

        if success:
            return "OK"
        else:
            return "Failed to send email"

    except Exception as e:
        print(f"Error in SendEmail handler: {e}")
        return f"Error: {str(e)}"
