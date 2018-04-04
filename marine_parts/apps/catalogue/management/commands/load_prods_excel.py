from django.core.management.base import BaseCommand, CommandError
from marine_parts.apps.categorizador.prods_excel import exec_excel_load


class Command(BaseCommand):
    help = 'Load products from json scraped data'

    def add_arguments(self, parser):
        parser.add_argument('filepaths', nargs='+')

        parser.add_argument(
            '--cat_base',
            action='store',
            dest='cat_base',
            default="Best Sellers > Extension Kits",
            help='Upper category where the created products are put.'
        )

        parser.add_argument(
            '--cat',
            action='store',
            required=True,
            dest='cat',
            help='Category where the created products belongs.'
        )

        parser.add_argument(
            '--manufacturer',
            action='store',
            dest='manufacturer',
            required=True,
            help='Name of the manufacturer for products loaded.'
        )

        parser.add_argument(
            '--origin',
            action='store',
            dest='origin',
            required=True,
            help='Name of the origin of the loaded products.'
        )

    def handle(self, *args, **options):
        total = 0

        cat_base = options['cat_base']
        self.stdout.write(self.style.WARNING('Using base category: %s.' % cat_base))

        cat = options['cat']
        self.stdout.write(self.style.WARNING('Category name: %s.' % cat))

        manufacturer = options['manufacturer']
        self.stdout.write(self.style.WARNING('Manufacturer name: %s.' % manufacturer))

        origin = options['origin']
        self.stdout.write(self.style.WARNING('Origin name: %s.' % origin))

        for filepath in options['filepaths']:
            self.stdout.write('Processing file %s. Please wait...' % filepath)
            try:
                nro = self.ejec(filepath, cat, cat_base, manufacturer, origin)
            except CommandError as ce:
                self.stderr.write(self.style.ERROR(ce.message.decode('utf-8') + ' Skipping...'))
                continue

            self.stdout.write(self.style.SUCCESS('%s products were created in DB from %s' % (nro, filepath)))

            total += nro

        if total > 0:
            self.stdout.write(self.style.SUCCESS('Total products created: %s' % total))
        else:
            self.stdout.write(self.style.WARNING('No products were created'))

    def ejec(self, filepath, cat, cat_base, nom_man, nom_ori):
        try:
            nro = exec_excel_load(filepath, cat, cat_base, nom_man, nom_ori)
        except Exception:
            import sys, traceback
            exc_info = sys.exc_info()
            traceback.print_tb(exc_info[2])
            print(exc_info[1])
            raise CommandError('An error occurred while processing this file: %s.' % filepath)

        return nro