from django.core.management.base import BaseCommand, CommandError
from marine_parts.apps.categorizador.categorizador import ejec_extraer_cats


class Command(BaseCommand):
    help = 'Retrieve categories from json scraped data. It only prints the categories found.'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+')

    def handle(self, *args, **options):

        filepaths = options.get('filepaths')
        if filepaths:
            for filepath in filepaths:
                self.stdout.write('Processing file %s. Please wait...' % filepath)
                try:
                    self.ejec(filepath)
                except CommandError as ce:
                    self.stderr.write(self.style.ERROR(ce.message.decode('utf-8') + ' Skipping...'))
                    continue
        else:
            self.stderr.write(self.style.ERROR('No filepaths were found. Operation cancelled'))


    def ejec(self, filepath):
        try:
            ejec_extraer_cats(filepath)
        except Exception:
            import sys, traceback
            exc_info = sys.exc_info()
            traceback.print_tb(exc_info[2])
            print(exc_info[1])
            raise CommandError('An error occurred while processing this file: %s' % filepath)
