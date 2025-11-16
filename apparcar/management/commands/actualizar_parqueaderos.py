import csv
from django.core.management.base import BaseCommand
from apparcar.models import Parking, Owner

FILE_PATH = "PARQUEADEROS_IBAGUE_GOOGLEMAPS_CORREGIDO.csv"

class Command(BaseCommand):
    help = "Actualiza parqueaderos existentes desde un CSV"

    def handle(self, *args, **kwargs):
        try:
            owner = Owner.objects.get(user__username="diego")
        except Owner.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ No existe Owner con user.username='diego'"))
            return

        with open(FILE_PATH, encoding="latin1") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                name = row["name"]

                # ❗ Aquí cambiamos get() por filter()
                parqueaderos = Parking.objects.filter(name=name)

                if not parqueaderos.exists():
                    self.stdout.write(self.style.WARNING(f"⚠ No existe '{name}', se salta..."))
                    continue

                for parking in parqueaderos:

                    parking.owner = owner
                    parking.latitude = row["latitude"].replace(",", ".")
                    parking.longitude = row["longitude"].replace(",", ".")
                    parking.car_spaces = int(row["car_spaces"])
                    parking.moto_spaces = int(row["moto_spaces"])
                    parking.opening_time = row["opening_time"]
                    parking.closing_time = row["closing_time"]
                    parking.car_rate = row["car_rate"]
                    parking.moto_rate = row["moto_rate"]
                    parking.nearby_place = row["nearby_place"]

                    parking.save()

                self.stdout.write(self.style.SUCCESS(f"✔ Actualizado(s): {name}  ({parqueaderos.count()} coincidencia/s)"))

        self.stdout.write(self.style.SUCCESS("🎉 Actualización completada"))
