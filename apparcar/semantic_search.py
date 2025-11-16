# apparcar/semantic_search.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from .models import Parking

# Lazy-load del modelo para acelerar arranque
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def _cosine_sim(a, b):
    # a, b: numpy arrays
    if a is None or b is None:
        return -1.0
    # normalizar por seguridad
    a = a / np.linalg.norm(a) if np.linalg.norm(a) != 0 else a
    b = b / np.linalg.norm(b) if np.linalg.norm(b) != 0 else b
    return float(np.dot(a, b))

def semantic_search(query: str, top_k: int = 10):
    """
    Devuelve lista de (Parking, score) ordenados por score descendente.
    """
    model = get_model()
    q_emb = model.encode(query, convert_to_numpy=True)

    # obtener parkings con embedding ya calculado
    parkings = Parking.objects.exclude(embedding__isnull=True)
    results = []
    for p in parkings:
        try:
            emb = p.embedding
            # emb puede ser list -> convertir a numpy
            emb_arr = np.array(emb, dtype=np.float32)
            score = _cosine_sim(q_emb, emb_arr)
            results.append((p, score))
        except Exception:
            continue

    # ordenar por score descendente y devolver top_k
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_k]
