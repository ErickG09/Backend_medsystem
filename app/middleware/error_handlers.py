import logging
from werkzeug.exceptions import HTTPException
from flask import jsonify

log = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException):
        payload = {
            "message": e.description or "HTTP error",
            "status": e.code,
        }
        return jsonify(payload), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e: Exception):
        log.exception("Unhandled exception")
        return jsonify({"message": "Internal server error"}), 500
