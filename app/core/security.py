import re

from flask import jsonify
from flask import current_app
from flask import request
from flask_wtf.csrf import CSRFError
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import generate_csrf

from app.core.logging_config import get_logger


class TestingAwareCSRFProtect(CSRFProtect):
    def protect(self, *args, **kwargs):
        if current_app.testing:
            return None
        return super().protect(*args, **kwargs)


csrf = TestingAwareCSRFProtect()
security_logger = get_logger("security")
POST_FORM_RE = re.compile(
    r"(<form\b(?=[^>]*\bmethod\s*=\s*['\"]?post\b)[^>]*>)",
    re.IGNORECASE,
)


def init_security(app):
    csrf.init_app(app)

    @app.after_request
    def aplicar_cabecalhos_e_csrf(response):
        response.headers.setdefault(
            "Content-Security-Policy",
            "; ".join((
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com",
                "font-src 'self' data: https://cdn.jsdelivr.net https://fonts.gstatic.com",
                "img-src 'self' data: blob:",
                "connect-src 'self'",
                "frame-ancestors 'self'",
                "object-src 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            )),
        )
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

        if response.status_code >= 400 or not response.mimetype == "text/html":
            return response
        html = response.get_data(as_text=True)
        if "<form" not in html.lower():
            return response
        token = generate_csrf()
        campo = f'<input type="hidden" name="csrf_token" value="{token}">'
        response.set_data(POST_FORM_RE.sub(r"\1" + campo, html))
        return response

    @app.errorhandler(CSRFError)
    def erro_csrf(erro):
        security_logger.warning("CSRF validation failed", extra={"operation": "CSRF_FALHA"})
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"erro": "Sessão expirada ou requisição inválida. Recarregue a página."}), 400
        return "Sessão expirada ou requisição inválida. Recarregue a página e tente novamente.", 400
