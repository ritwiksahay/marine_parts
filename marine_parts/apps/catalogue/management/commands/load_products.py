from django.core.management.base import BaseCommand, CommandError
from marine_parts.apps.categorizador.categorizador import ejec_cargador

class Command(BaseCommand):
    help = 'Load products from json scraped data'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+')

    def handle(self, *args, **options):
        for filepath in options['filepaths']:
            nro = 0
            try:
                nro += ejec_cargador(filepath)
            except Exception:
                raise CommandError('An error occurred while processing this file: %s' % filepath)

            self.stdout.write(self.style.SUCCESS('%s products were created in DB from %s' % (nro, filepath)))

