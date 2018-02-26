from django.core.management.base import BaseCommand, CommandError
from marine_parts.apps.categorizador.categorizador import ejec_cargador

class Command(BaseCommand):
    help = 'Load products from json scraped data'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+')

    def handle(self, *args, **options):
        total = 0
        for filepath in options['filepaths']:

            nro = 0
            try:
                self.stdout.write('Processing file %s. Please wait...' % filepath)
                nro += ejec_cargador(filepath)
            except Exception:
                raise CommandError('An error occurred while processing this file: %s' % filepath)

            self.stdout.write(self.style.SUCCESS('%s products were created in DB from %s' % (nro, filepath)))
            total += nro

        self.stdout.write(self.style.SUCCESS('Total products created: %s' % total))

