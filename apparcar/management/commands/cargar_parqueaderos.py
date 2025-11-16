import csv
from django.core.management.base import BaseCommand
from apparcar.models import Parking, Owner

FILE_PATH = "PARQUEADEROS_IBAGUE_GOOGLEMAPS_CORREGIDO.csv"

class Command(BaseCommand):
    help = "Carga o actualiza parqueaderos desde CSV"

    def handle(self, *args, **kwargs):

        try:
            with open(FILE_PATH, encoding="latin1") as f:
                reader = csv.DictReader(f, delimiter=";")

                print("Columnas encontradas:", reader.fieldnames)

                for row in reader:
                    name = row["name"].strip()

                    # Convertir coordenadas: comas → puntos
                    latitude = row["latitude"].replace(",", ".").strip()
                    longitude = row["longitude"].replace(",", ".").strip()

                    # Asegurar longitud negativa
                    if not longitude.startswith("-"):
                        longitude = "-" + longitude

                    car_spaces = int(row["car_spaces"])
                    moto_spaces = int(row["moto_spaces"])

                    # Asumimos que el propietario es tu usuario "diego"
                    owner = Owner.objects.get(user__username="diego")

                    parking, created = Parking.objects.update_or_create(
                        name=name,
                        defaults={
                            "owner": owner,
                            "latitude": latitude,
                            "longitude": longitude,
                            "car_spaces": car_spaces,
                            "moto_spaces": moto_spaces,
                            "opening_time": row["opening_time"],
                            "closing_time": row["closing_time"],
                            "car_rate": row["car_rate"],    # ya corregido manualmente
                            "moto_rate": row["moto_rate"],
                            "nearby_place": row["nearby_place"],
                        },
                    )

                    if created:
                        print(f"✔ Creado: {name}")
                    else:
                        print(f"✔ Actualizado: {name}")

                print("\nProceso completado.")

        except Exception as e:
            print(f"❌ Error: {e}")
