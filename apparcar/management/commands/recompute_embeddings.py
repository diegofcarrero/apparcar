from django.core.management.base import BaseCommand
from apparcar.models import Parking
from apparcar.signals import ensure_embedder, make_parking_text
import gc
import torch

class Command(BaseCommand):
    help = "Recalcula embeddings para todos los parkings existentes."

    def handle(self, *args, **kwargs):
        model = ensure_embedder()
        parkings = Parking.objects.all()

        self.stdout.write(self.style.WARNING(f"Recalculando embeddings para {parkings.count()} parqueaderos..."))

        for parking in parkings:
            try:
                text = make_parking_text(parking)
                emb = model.encode(text, convert_to_numpy=True).tolist()
                parking.embedding = emb
                parking.save(update_fields=['embedding'])
                self.stdout.write(self.style.SUCCESS(f"✓ Parking {parking.id} actualizado"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error en Parking {parking.id}: {e}"))

        self.stdout.write(self.style.SUCCESS("FIN: Todos los embeddings fueron recalculados."))

        # 🔥 FIX PARA EVITAR "terminate called without active exception"
        try:
            del model
        except:
            pass

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        gc.collect()
