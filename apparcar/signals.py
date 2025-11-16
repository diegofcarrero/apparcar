# apparcar/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Parking
import threading

# importamos el generador en lazy-load para no bloquear import time en Django boot
def get_embedder():
    from sentence_transformers import SentenceTransformer
    # modelo ligero recomendado
    return SentenceTransformer('all-MiniLM-L6-v2')

_embedder = None
_embedder_lock = threading.Lock()

def ensure_embedder():
    global _embedder
    with _embedder_lock:
        if _embedder is None:
            _embedder = get_embedder()
    return _embedder

def make_parking_text(parking: Parking):
    """
    Texto combinado para representar semánticamente un parking.
    Ajusta/añade campos que quieras incluir (tarifas, horario, etc.).
    """
    parts = [
        parking.name or "",
        parking.nearby_place or "",
        f"{parking.car_spaces} carros",
        f"{parking.moto_spaces} motos",
        f"tarifa carro {parking.car_rate}" if parking.car_rate is not None else "",
        f"tarifa moto {parking.moto_rate}" if parking.moto_rate is not None else "",
    ]
    return " . ".join([p for p in parts if p])

@receiver(post_save, sender=Parking)
def compute_parking_embedding(sender, instance: Parking, **kwargs):
    """
    Cada vez que un Parking se crea o actualiza, recalculamos embedding.
    Lo hacemos en hilos para no bloquear demasiado la request.
    """
    def _compute_and_save(parking_id):
        try:
            p = Parking.objects.get(pk=parking_id)
            text = make_parking_text(p)
            model = ensure_embedder()
            emb = model.encode(text, convert_to_numpy=True).tolist()
            # guardamos lista de floats en JSONField
            p.embedding = emb
            p.save(update_fields=['embedding'])
        except Exception as e:
            # opcional: loggear
            import logging
            logging.exception("Error calculando embedding para Parking %s: %s", parking_id, e)

    # calculamos en background para no demorar la respuesta HTTP
    threading.Thread(target=_compute_and_save, args=(instance.id,), daemon=True).start()
