from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from triggers.pl_python.builder import pl_functions, install_function


class Command(BaseCommand):
    help = 'Syncs PL/Python functions, decorated with @plfunction'

    def delete_function(self):
        raise NotImplemented

    @transaction.atomic
    def handle(self, *args, **options):
        if not pl_functions:
            self.stdout.write("No PL/Python functions found")

        for function_name, f in pl_functions.items():
            self.stdout.write(f"Synching {function_name}")
            install_function(f)
            self.stdout.write(f"Installed {function_name}")

