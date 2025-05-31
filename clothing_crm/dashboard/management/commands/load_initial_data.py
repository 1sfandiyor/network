from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Loads initial data for the Clothing CRM'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Loading initial data...'))

        # Load fixtures
        call_command('loaddata', 'initial_data')

        self.stdout.write(self.style.SUCCESS('Initial data loaded successfully!'))