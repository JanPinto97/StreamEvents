from django.core.management.base import BaseCommand
from django.utils import timezone

from events.models import Event


class Command(BaseCommand):
    help = "Actualitza automàticament els estats dels esdeveniments (scheduled -> live, live -> finished)."

    def handle(self, *args, **options):
        now = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.write(self.style.NOTICE(f"Inici actualització d'estats ({now})..."))

        scheduled_updated, finished_count = Event.update_statuses()

        self.stdout.write(self.style.SUCCESS(
            f"Actualització completada: "
            f"{scheduled_updated} esdeveniment(s) programat(s) passat(s) a 'live', "
            f"{finished_count} esdeveniment(s) 'live' passat(s) a 'finished'."
        ))
