from flask import request, current_app, abort

def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if not current_app.debug:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

def enforce_origin_host():
    # Permite sin Origin (curl/Postman), valida cuando venga
    allowed = set(current_app.config.get("CORS_ORIGINS", []))
    origin = request.headers.get("Origin")
    if origin and origin not in allowed:
        abort(403, description="Origin no permitido")

    # Hardening sencillo de Host (opcional)
    # Render usa *.onrender.com; en local permitimos hosts locales.
    host = (request.host or "").split(":")[0]
    if current_app.debug:
        return
    if host.endswith(".onrender.com") or host in {"localhost", "127.0.0.1"}:
        return
    # Si tienes un dominio propio, añádelo aquí:
    # if host == "api.tudominio.com": return
