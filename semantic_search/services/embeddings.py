import threading
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_lock = threading.Lock()
_model = None


def get_model():
    """
    Carrega el model una sola vegada (lazy loading).
    Thread-safe.
    """
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed_text(text: str) -> list[float]:
    """
    Converteix un text en un embedding (llista de floats).
    """
    text = (text or "").strip()
    if not text:
        return []

    model = get_model()
    vec = model.encode([text], normalize_embeddings=True)[0]
    return vec.tolist()


def model_name() -> str:
    return _MODEL_NAME
