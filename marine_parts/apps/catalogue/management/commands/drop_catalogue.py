"""."""
from django.core.management.base import BaseCommand, CommandError
from marine_parts.apps.catalogue.drop_catalogue import execute

class Command(BaseCommand):
    help = 'Delete products and non-base categories'

    def handle(self, *args, **options):
        try:
            num_prods_deleted = execute()
        except Exception as e:
            print(e)
            raise CommandError("An error occurred while "
                               "executing this command")

        self.stdout.write(
            self.style.SUCCESS(
                "%s products were deleted in DB." %
                (num_prods_deleted)))
