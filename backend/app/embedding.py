from sentence_transformers import SentenceTransformer
from app.config import settings

_model: SentenceTransformer | None = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model_name)
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    return get_model().encode(texts, normalize_embeddings=True).tolist()

def embed_query(q: str) -> list[float]:
    return embed_texts([q])[0]