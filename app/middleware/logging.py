import logging
import sys
import uuid
from flask import g, request

def setup_logging(app):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

    @app.before_request
    def inject_request_id():
        g.request_id = str(uuid.uuid4())
        app.logger.info(
            "REQ %s %s %s %s",
            g.request_id,
            request.method,
            request.path,
            request.remote_addr,
        )

    @app.after_request
    def log_response(resp):
        app.logger.info(
            "RES %s %s %s",
            g.get("request_id", "-"),
            resp.status_code,
            resp.content_type,
        )
        # Seguridad básica
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-XSS-Protection", "0")
        return resp
