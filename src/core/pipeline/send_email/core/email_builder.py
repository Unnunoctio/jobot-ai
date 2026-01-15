from typing import Any, Dict, List


class EmailBuilder:
    """Handles building HTML emails for job offers."""

    @staticmethod
    def build_html(offers: List[Dict[str, Any]]) -> str:
        """Build HTML email from list of offers."""

        header = EmailBuilder._build_header(len(offers))
        offer_items = "".join([EmailBuilder._build_offer_item(o) for o in offers])
        footer = EmailBuilder._build_footer()

        return f"""
        <div style="font-family: Arial, sans-serif; color: #222; max-width: 600px; margin: auto;">
            {header}
            <ul style="list-style: none; padding: 0;">
                {offer_items}
            </ul>
            {footer}
        </div>
        """

    @staticmethod
    def _build_header(count: int) -> str:
        """Build HTML header for email."""

        return f"""
        <h2 style="text-align: center; color: #2b6cb0;">
            {count} {'Oferta' if count == 1 else 'Ofertas'} de Trabajo {'Encontrada' if count == 1 else 'Encontradas'}
        </h2>
        <p style="color: #444; text-align: center;">
            Estas son las oportunidades que coinciden con tu perfil 👇
        </p>
        """

    @staticmethod
    def _build_offer_item(offer: Dict) -> str:
        """Build HTML for a single offer."""
        return f"""
        <li style="
            background: #f9fafb;
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border-left: 5px solid #2b6cb0;
        ">
            <h3 style="margin: 0 0 8px 0; color: #2b6cb0;">{offer.get('title', 'Sin título')}</h3>
            <p style="margin: 4px 0;"><strong>Empresa:</strong> {offer.get('company', 'Unknown')}</p>
            <p style="margin: 4px 0;"><strong>Ubicación:</strong> {offer.get('location', 'Unknown')}</p>
            <p style="margin: 4px 0;"><strong>Modalidad:</strong> {offer.get('modality', 'Unknown')}</p>
            <p style="margin: 4px 0;"><strong>Fecha Publicación:</strong> {offer.get('created_at', 'Unknown')}</p>
            <p style="margin: 4px 0;"><strong>N° de Postulaciones:</strong> {offer.get('applications', 'n/a')}</p>
            <p style="margin: 4px 0;"><strong>Puntuación IA:</strong>
                <span style="color: {EmailBuilder._get_score_color(offer.get('score', 0))}; font-weight: bold;">
                    {offer.get('score', 0)}/100
                </span>
            </p>
            <p style="margin-top: 10px;">
                <a href="{offer.get('url', '#')}" style="
                    background: #2b6cb0;
                    color: #fff;
                    padding: 10px 14px;
                    text-decoration: none;
                    border-radius: 6px;
                    display: inline-block;
                ">
                    Ver oferta ({offer.get('spider', 'Unknown')})
                </a>
            </p>
        </li>
        """

    @staticmethod
    def _get_score_color(score: int) -> str:
        """Get color based on score."""
        if score >= 80:
            return "#059669"  # Green
        elif score >= 60:
            return "#d97706"  # Orange
        else:
            return "#dc2626"  # Red

    @staticmethod
    def _build_footer() -> str:
        """Build email footer."""
        return """
        <p style="margin-top: 20px; text-align: center; color: #555;">
            ¡Gracias por utilizar <strong>Jobot AI</strong>! 🚀
        </p>
        """
