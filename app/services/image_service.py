from ..models.file_asset import FileKind
from .storage_service import normalize_url

def validate_and_prepare(kind: FileKind, url: str) -> tuple[str, str | None]:
    """
    Por ahora solo URLs: normaliza y sugiere mime_type por extensión.
    Retorna (url_normalizada, mime_type_sugerido).
    """
    u = normalize_url(url)

    low = u.lower()
    if low.endswith(".pdf"):
        mime = "application/pdf"
    elif low.endswith(".webp"):
        mime = "image/webp"
    elif low.endswith(".jpg") or low.endswith(".jpeg"):
        mime = "image/jpeg"
    elif low.endswith(".png"):
        mime = "image/png"
    else:
        # Rechazamos extensiones desconocidas desde schema; aquí vamos seguros
        mime = None

    # Recomendación: para fotos clínicas preferimos .webp por peso/calidad
    return u, mime
