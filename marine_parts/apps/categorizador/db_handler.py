import os
import urllib

from django.conf import settings
from django.core.files import File
from django.db import transaction, IntegrityError, DatabaseError

from datetime import datetime
from oscar.apps.catalogue.models import ProductClass, ProductAttribute
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.partner.models import StockRecord, Partner
from decimal import Decimal as D

from marine_parts.apps.catalogue.models import Product, ReplacementProduct, ProductCategory


# Interface
class DBHandler:

    def add_part_number(self, part_number_v):
        pass

    def crear_categoria(self, breadcrumb, comp_img=None):
        pass

    def obt_subcomponent_class(self):
        pass

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, product_class):
        pass

    def crear_prods(self, cat, is_aval, prod_name,
                    part_num_v, manufac_v, orig_v,
                    diag_num_v, price_excl_tax, price_retail, cost_price):
        pass


class DBAccess(DBHandler):

    def __init__(self, cat_base):
        self.subcomp_class = self.obt_subcomponent_class()
        self.part_number, self.manufacturer, self.origin = \
            self.obt_crea_atributos_prods(self.subcomp_class)
        self.partner = self.obt_partner()
        self.part_number_set = set()
        self.cat_base = cat_base.strip() + ' > '

    def add_part_number(self, part_number_v):
        self.part_number_set.add(part_number_v)

    def check_partnumber(self, part_number_v):
        try:
            prod = Product.objects.get(attribute_values__value_text=part_number_v)
        except Product.MultipleObjectsReturned:
            print("Offending product part number: %s" % part_number_v)
            raise
        except Product.DoesNotExist:
            prod = None

        if part_number_v in self.part_number_set:
            return prod, True
        elif prod:
            self.add_part_number(part_number_v)
            return prod, True
        else:
            return prod, False

    def crear_categoria(self, breadcrumb, comp_img=None):
        path = self.cat_base + ' > '.join(breadcrumb[1:])

        try:
            cat = create_from_breadcrumbs(path)
        except IntegrityError:
            print("Offending category: %s" % path)
            raise

        if comp_img:
            try:
                url = os.path.join(settings.SCRAPPER_ROOT, comp_img)
                result = urllib.urlretrieve(url)
                cat.diagram_image.save(
                    comp_img,
                    File(open(result[0]))
                )
                cat.save()

            except Exception as e:
                print(e)

        return cat

    def obt_subcomponent_class(self):
        return self.obt_crea_prod_class('Subcomponent')

    def obt_partner(self):
        partner, _ = Partner.objects.get_or_create(name='Loaded')
        return partner

    def obt_crea_prod_class(self, nom):
        product_class, _ = ProductClass.objects.get_or_create(name=nom)
        return product_class

    def asign_prod_replacement(self, p_origin, p_asign):
        ReplacementProduct.objects.get_or_create(primary=p_origin,
                                                 replacement=p_asign)
        return

    def add_product_to_category(self, prod, cat, diag_number):
        try:
            with transaction.atomic():
                ProductCategory.objects.create(product=prod, category=cat, diagram_number=diag_number)
        except IntegrityError:
            pass
        except DatabaseError:
            print('Offending data (%s, %s, %s)' % (prod.title, cat.name, diag_number))
            raise

    def add_stock_records(self, pro, part_number, amount, price_excl_tax, price_retail, cost_price):
        StockRecord.objects.create(
            product=pro,
            partner=self.partner,
            partner_sku=part_number + str(datetime.now()),
            price_excl_tax=price_excl_tax,
            price_retail=price_retail,
            cost_price=cost_price,
            num_in_stock=amount)

    def obt_crea_atributos_prods(self, product_class):
        manufacturer, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class,
            name='Manufacturer',
            code='M', required=True,
            type=ProductAttribute.TEXT)
        origin, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class,
            name='Origin',
            code='O',
            required=False,
            type=ProductAttribute.TEXT)
        part_number, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class,
            name='Part number',
            code='PN',
            required=True,
            type=ProductAttribute.TEXT)

        return part_number, manufacturer, origin

    def crear_prods(self, cat, is_aval, prod_name,
                    part_num_v, manufac_v, orig_v,
                    diag_num_v, price_excl_tax, price_retail, cost_price):

        item = Product.objects.create(product_class=self.subcomp_class,
                                      title=prod_name)
        if part_num_v:
            self.part_number.save_value(item, part_num_v)
            item.upc = part_num_v
            item.save()
        else:
            raise RuntimeError('Part Number does not exists')

        if manufac_v:
            self.manufacturer.save_value(item, manufac_v)
        if orig_v:
            self.origin.save_value(item, orig_v)

        try:
            ProductCategory.objects.create(product=item, category=cat,
                                       diagram_number=diag_num_v)
        except DatabaseError:
            print('Offending data (%s, %s, %s)' % (item.title, cat.name, diag_num_v))
            raise

        if is_aval:
            self.add_stock_records(item, part_num_v, 1000, price_excl_tax, price_retail, cost_price)

        return item