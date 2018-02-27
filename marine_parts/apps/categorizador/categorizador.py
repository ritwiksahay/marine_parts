#
#   Creador: Daniel Leones
#   Descripcion: Extrae las categorias  y los productos de los archivos JSON
#                usando un version simplificada de DFS. Se imprime por
#                salida estandar los resultados en la notacion jerarquica de Oscar.
#   Fecha: 7/12/2017
#   Modificado: 26/02/2017
#   Ejecucion: dentro del shell de Django. Usar extraer_prods. Este devuelve el
#              numero de productos que encuentra. Por otra parte, crea las
#              categorias, atributos, la clase de producto, y los valores de
#              los atributos.
#
import json
import os
import urllib

from django.conf import settings
from django.core.files import File

from datetime import datetime
from oscar.apps.catalogue.models import (ProductClass,
                                         ProductCategory,
                                         ProductAttribute)
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.apps.partner.models import StockRecord, Partner
from marine_parts.apps.catalogue.models import Product, ReplacementProduct
from decimal import Decimal as D

# Necesario para controlar que se introduce en la BD
from django.db.transaction import atomic


class IOHandler:

    def leer(self, nomArch):
        pass


class FileHandler(IOHandler):

    # Manejo de excepciones de I/O
    def leer(self, nomArch):
        return json.load(open(nomArch, 'r'))


class DBHandler:

    def crear_categoria(self, breadcrumb, comp_img=None):
        pass

    def obt_subcomponent_class(self):
        pass

    def asign_prod_replacement(self, p_origin, p_asign):
        pass

    def obt_crea_atributos_prods(self, product_class):
        pass

    def crear_prods(self, cat, is_aval, prod_name, part_num_v, manufac_v, diag_num_v):
        pass


class DBAccess(DBHandler):

    def __init__(self, cat_base):
        self.subcomp_class = self.obt_subcomponent_class()
        self.part_number, self.manufacturer, self.diag_number = \
            self.obt_crea_atributos_prods(self.subcomp_class)
        self.partner = self.obt_partner()
        self.part_number_set = set()
        self.cat_base = cat_base + '>'

    def add_part_number(self, part_number_v):
        self.part_number_set.add(part_number_v)

    def check_partnumber(self, part_number_v):
        return part_number_v in self.part_number_set

    def crear_categoria(self, breadcrumb, comp_img=None):
        path = self.cat_base + ' > '.join(breadcrumb[1:])
        cat = create_from_breadcrumbs(path)
        if comp_img:
            try:
                url = os.path.join(settings.SCRAPPER_ROOT, comp_img)
                result = urllib.urlretrieve(url)
                cat.diagram_image.save(
                    os.path.basename(url),
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
        ReplacementProduct.objects.create(primary=p_asign,
                                          replacement=p_origin)

    def add_product_to_category(self, part_number_v, cat):
        prod = Product.objects.get(attribute_values__value_text=part_number_v)
        ProductCategory.objects.create(product=prod, category=cat)
        return prod

    def add_stock_records(self, pro, amount):
        StockRecord.objects.create(
            product=pro,
            partner=self.partner,
            partner_sku=pro.title + str(datetime.now()),
            price_excl_tax=D(0.00),
            price_retail=D(0.00),
            cost_price=D(0.00),
            num_in_stock=amount)

    def obt_crea_atributos_prods(self, product_class):
        manufacturer, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class,
            name='Manufacturer',
            code='M', required=True,
            type=ProductAttribute.TEXT)
        part_number, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class,
            name='Part number',
            code='PN',
            required=True,
            type=ProductAttribute.TEXT)
        diag_number, _ = ProductAttribute.objects.get_or_create(
            product_class=product_class,
            name='Diagram number',
            code='DN',
            required=True,
            type=ProductAttribute.TEXT)

        return part_number, manufacturer, diag_number

    def crear_prods(self, cat, is_aval, prod_name, part_num_v, manufac_v, diag_num_v):
        item = Product.objects.create(product_class=self.subcomp_class, title= prod_name)

        if part_num_v:
            self.part_number.save_value(item, part_num_v)
        if manufac_v:
            self.manufacturer.save_value(item, manufac_v)
        if diag_num_v:
            self.diag_number.save_value(item, diag_num_v)

        item.save()

        ProductCategory.objects.create(product=item, category=cat)

        if is_aval:
            self.add_stock_records(item, 1000)

        return item


########################################################################################################################
@atomic()
def nav_prods(json_products, bre_cat, db_oscar):
    """
    Crea los productos que se encuentre en el JSON en la BD del proyecto.
    Devuelve el numero de productos procesados.
    """

    def obt_sucesores(hijo):
        products = hijo.get('products')
        if products:
            return products

        products = hijo.get('replacements')
        if products:
            return products

        return None

    comp_img = json_products.get('image')
    cat = db_oscar.crear_categoria(bre_cat, comp_img)

    pila = list()
    pila.append((json_products, None))
    nro_products = 0

    while pila:
        prod_json, padr = pila.pop()
        sucesores = obt_sucesores(prod_json)

        pro = None
        prod_name = prod_json.get('product')
        if prod_name:
            is_available = prod_json.get('is_available')
            part_number_v = prod_json.get('part_number')
            manufacturer_v = prod_json.get('manufacturer')
            diagram_number_v = prod_json.get('diagram_number')


            if db_oscar.check_partnumber(part_number_v):
                ppp = db_oscar.add_product_to_category(part_number_v, cat)
            else:
                pro = db_oscar.crear_prods(cat, is_available, prod_name, part_number_v, manufacturer_v, diagram_number_v)
                db_oscar.add_part_number(part_number_v)
                nro_products += 1

                if padr:
                    db_oscar.asign_prod_replacement(padr, pro)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, pro))

    return nro_products

########################################################################################################################

def obt_sucesores(hijo):
    suc_cat = hijo.get('categories')
    if suc_cat:
        return suc_cat

    suc_sub_cat = hijo.get('sub_category')
    if suc_sub_cat:
        return suc_sub_cat

    return None


def obt_nombres(hijo):
    sucs_nom = hijo.get('category')
    if sucs_nom:
        return sucs_nom
    else:
        return ''


def extraer_prods(json_categorias, db):
    return extraer_prods_aux(json_categorias, db)

def extraer_prods_aux(json_categorias, db):
    pila = list()
    pila.append((json_categorias, ''))
    camino = list()
    nro_products = 0

    while pila:
        hijo, _ = pila.pop()
        sucesores = obt_sucesores(hijo)
        nom_hijo = obt_nombres(hijo).strip()
        camino.append(nom_hijo)
        # print('\nHijo: ', nom_hijo)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, nom_hijo))
        else:
            # Agregar o crear categorias
            nro_products += nav_prods(hijo, list(camino), db)

            if pila:
                # print('camino antes' , camino)
                _, padre = pila[-1]
                while camino[-1] != padre:
                    camino.pop()
                # print('camino despues', camino)

    return nro_products


def extraer_cats(json_categorias):
    pila = list()
    pila.append((json_categorias, ''))
    categorias = list()
    camino = list()

    while pila:
        hijo, _ = pila.pop()
        sucesores = obt_sucesores(hijo)
        nom_hijo = obt_nombres(hijo).strip()
        camino.append(nom_hijo)

        if sucesores:
            for suc in sucesores:
                pila.append((suc, nom_hijo))
        else:
            # Agregar o crear categorias
            categorias.append(list(camino))

            if pila:
                _, padre = pila[-1]
                while camino[-1] != padre:
                    camino.pop()

    categorias.reverse()
    return categorias


def aNotJerarquica(list):
    xs = []
    for li in (list):
        lit = ' > '.join(li[1:])
        xs.append(lit)

    return xs


def imprimirCate(categorias):
    print('Categorias encontradas')
    for cat in categorias:
        print(cat)


def ejec_cargador(caminoArch, cat_base):
    fh = FileHandler()
    db = DBAccess(cat_base)
    return extraer_prods(fh.leer(caminoArch), db)
