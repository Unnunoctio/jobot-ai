import resend


class EmailSender:
    """Handles sending emails via Resend."""

    def __init__(self, api_key: str):
        resend.api_key = api_key

    def send(self, to: str, subject: str, html: str) -> bool:
        """Send email via Resend."""

        params: resend.Emails.SendParams = {
            "from": "Jobot AI <onboarding@resend.dev>",
            "to": to,
            "subject": subject,
            "html": html,
        }

        try:
            response = resend.Emails.send(params)
            print(f"Email sent successfully: {response}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
