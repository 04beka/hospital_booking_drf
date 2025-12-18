from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time, datetime
from apps.doctors.models import Doctor, AvailabilitySlot

class Command(BaseCommand):
    help = "Seed demo doctors and 7-day availability slots (60 min)."

    def handle(self, *args, **options):
        doctors = [
            ("Nino", "Beridze", "Cardiology", "101"),
            ("Giorgi", "Kapanadze", "Neurology", "102"),
            ("Mariam", "Tsereteli", "Dermatology", "103"),
            ("Dato", "Gogoladze", "Orthopedics", "104"),
            ("Ana", "Gelashvili", "Pediatrics", "105"),
        ]

        created_doctors = []
        for fn, ln, sp, room in doctors:
            doc, _ = Doctor.objects.get_or_create(first_name=fn, last_name=ln, defaults={"specialty": sp, "room": room})
            doc.specialty = sp
            doc.room = room
            doc.is_active = True
            doc.save()
            created_doctors.append(doc)

        now = timezone.localtime(timezone.now())
        start_date = (now + timedelta(days=1)).date()  # start from tomorrow

        # working hours: 10:00 to 17:00 (7 slots)
        work_start = time(10, 0)
        slots_per_day = 7

        created = 0
        for doc in created_doctors:
            for d in range(7):
                day = start_date + timedelta(days=d)
                day_start_dt = timezone.make_aware(datetime.combine(day, work_start))
                for i in range(slots_per_day):
                    st = day_start_dt + timedelta(hours=i)
                    _, was_created = AvailabilitySlot.objects.get_or_create(
                        doctor=doc,
                        start_time=st,
                        defaults={"duration_minutes": 60, "is_available": True},
                    )
                    if was_created:
                        created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete: {len(created_doctors)} doctors, {created} slots created."))
