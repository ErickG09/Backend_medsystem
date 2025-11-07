from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    """
    Limpia espacios, asegura esquema y remueve fragmentos inútiles.
    No descarga ni valida existencia, solo normaliza la forma.
    """
    u = url.strip()
    parsed = urlparse(u)
    if not parsed.scheme:
        # Si no viene esquema, asumimos https (puedes cambiar a http si tu origen lo usa)
        parsed = parsed._replace(scheme="https")
    # limpiamos fragmentos (#) pero dejamos query (tokens firmados, etc.)
    parsed = parsed._replace(fragment="")
    return urlunparse(parsed)
