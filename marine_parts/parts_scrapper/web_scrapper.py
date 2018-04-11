# -*- coding: utf-8 -*-

import argparse
import copy
from datetime import date
import errno
from functools import partial
import json
from lxml import etree, html
import os
import re
import requests
import textwrap
from urlparse import urlparse as parse

from django.utils.text import slugify

# CONSTANT DEFINITIONS
FILE_DIR = os.path.dirname(os.path.realpath(__file__))
BOATSNET_BASE_URL = 'http://www.boats.net'
MARINE_ENGINE_BASE_URL = 'https://www.marineengine.com'
MARINE_EXPRESS_BASE_URL = 'http://www.marinepartsexpress.com'
MARINE_PARTS_EUROPE_BASE_URL = 'http://www.marinepartseurope.com'
INIT_OFFSET = 0
INIT_OFFSET_2 = 0
PRETTY_OUTPUT = False
THREADED = False
THREADS = 1


def create_output_file(data, path):
    """Dump the json data into a file."""
    data['scraping_successful'] = True
    # Check if the path exists, if not create it
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        # Guard against race condition
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(path, 'w') as outfile:
        if PRETTY_OUTPUT:
            json.dump(data, outfile, indent=4)
        else:
            json.dump(data, outfile, separators=(',', ':'))
    data['sub_category'] = []


def request_get(path, stream=False):
    """Execute a GET request and returns contents."""
    try:
        return requests.get(path, stream=stream)
    except Exception as e:
        print(e)


def get_product_title(text, part_number):
    """Extract part's title from text."""
    pn = re.sub('[\s-]', '', part_number)

    def comp(s):
        return pn not in re.sub('[\s-]', '', s) and s != 'Priced Individually'

    lis = text.split(" - ")
    new = filter(comp, lis)
    return ' - '.join(new)

##################################################################
# MARINE PARTS EUROPE WEB ########################################
##################################################################




def marinepartseurope_volvo_penta_scrapper(begin=0, end=None):
    """Scrapper for Marine Parts Europe Volvo Penta Parts."""
    global MARINE_PARTS_EUROPE_BASE_URL, FILE_DIR

    print('Starting Marine Parts Europe Volvo Penta Scrapping...')

    output_root_path = FILE_DIR + '/marine_europe/volvo/'
    images_root_folder = 'img/marine_europe/volvo/'

    # Get Index Page
    page = request_get(MARINE_PARTS_EUROPE_BASE_URL)
    tree = html.fromstring(page.content)

    # The selectors goes here so they dont recreate on every cicle
    xpath_selector = ("//table[@width='301']//tr[@class='cartItems']"
                      "/td[2]/a")

    mod_selector = ("//td[@class='bookCell']/h2/a")
    comp_selector = ("//div[@id='ctl00_PageContent_EPCCategories']/"
                     "table[1]//tr")
    ximg_selector = "//img[@id='ctl00_PageContent_PentaMap101']"
    diagram_number_selector = ("//div[@id='ctl00_PageContent_PentaPanel']/"
                               "table/tbody")

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    for cat in tree.xpath(xpath_selector)[3:4]:
        cat_name = cat.text
        cat_slug = slugify(cat_name)

        print("Scrapping category '%s'\n" % (cat_name))

        category = {
            'category_name': 'category',
            'category': cat_name,
            'sub_category': []
        }

        catalog['categories'].append(category)

        cat_link = cat.get('href')

        # Get Models Page
        page = request_get(
            MARINE_PARTS_EUROPE_BASE_URL +
            '/' + cat_link)
        tree = html.fromstring(page.content)

        mods = tree.xpath(mod_selector)[begin:end]
        num_mods = len(mods) + begin

        for idx, mod in enumerate(mods):
            mod_name = re.sub(r'[\n\t]+', '', mod.text)
            mod_slug = slugify(mod_name)
            print("'%s' starting... (%d of %d categories... %.2f %%)\n" %
                  (mod_name,
                   begin + idx,
                   num_mods,
                   float(begin + idx) / float(num_mods) * 100))

            mod_link = mod.get('href')

            model = {
                'category_name': 'model',
                'category': mod_name,
                'sub_category': []
            }

            # Get Components Page
            page = request_get(
                MARINE_PARTS_EUROPE_BASE_URL +
                '/' + mod_link)
            tree = html.fromstring(page.content)
            section = {}
            last_comp_slug = None
            sect_name = None

            for comp in tree.xpath(comp_selector):

                # Section Header
                if (comp.xpath("td[@class='catalogHeaderCell']/h2")):
                    # Components with same name can occur
                    # so we have to append a counter to the
                    # component name so it can be unique
                    # and don't cause inconsistency in the DB 
                    rep_component_counter = 0
                    # Save Previous section
                    if section != {}:
                        model['sub_category'].append(section)
                    sect_name = comp.xpath(
                        "td[@class='catalogHeaderCell']/h2")[0].text
                    rep_counter = 0
                    # if section title is empty, ignore
                    if not sect_name:
                        continue
                    section = {
                        'category_name': 'section',
                        'category': sect_name.strip(),
                        'sub_category': []
                    }
                # Component entry
                else:
                    # if section title is empty, ignore
                    if not sect_name:
                        continue

                    comp_a = comp.xpath(
                        "td[@class='catalogCell']/span/a")[0]
                    comp_name = comp_a.xpath('h3')[0].text.strip()
                    comp_link = comp_a.get('href')

                    # get related model serial
                    rel_model = comp.xpath(
                        "td[2]/a")[0].text
                    if rel_model:
                        comp_name += ' - ' + rel_model.strip()

                    # handle case where components names are equal
                    comp_slug = slugify(comp_name)

                    if comp_slug == last_comp_slug:
                        rep_counter += 1
                        comp_name += " - v%d" % (rep_counter + 1)
                    else:
                        rep_counter = 0

                    last_comp_slug = comp_slug
                    comp_slug = slugify(comp_name)

                    # print("Scrapping section '%s' component '%s' \n\turl: %s"
                    #       % (sect_name, comp_name, comp_link))

                    # Build component
                    component = {
                        'category_name': 'component',
                        'category': comp_name,
                        'products': [],
                    }

                    # Scrap component parts
                    page = request_get(
                        MARINE_PARTS_EUROPE_BASE_URL +
                        '/' + comp_link)
                    tree = html.fromstring(page.content)

                    # Download Component Image
                    component_image = MARINE_PARTS_EUROPE_BASE_URL
                    component_image += tree.xpath(ximg_selector)[0] \
                        .get('src')

                    r = request_get(component_image, stream=True)
                    image_rel_path = images_root_folder + \
                        mod_slug[0:64] + '/' + \
                        comp_slug[0:64] + '.gif'
                    image_final_path = os.path.join(FILE_DIR,
                                                    image_rel_path)
                    save_downloaded_file(image_final_path, r)
                    component_image = image_rel_path

                    component['image'] = component_image

                    for dn in tree.xpath(diagram_number_selector):

                        diagram_number = ''
                        product = {}
                        last_replaced = None
                        # Rows in a diagram_number table
                        for prod in dn.xpath('tr'):

                            try:
                                # if any of the following info is missing,
                                # then ignore part

                                # Get Diagram Number
                                try:
                                    diagram_number = \
                                        prod.xpath('td[1]')[0].text \
                                        if prod.xpath('td[1]')[0] \
                                            .text.strip() != '' \
                                        else diagram_number
                                    if not diagram_number:
                                            diagram_number = '0'
                                except IndexError:
                                    continue
                                except AttributeError:
                                    pass

                                # Get Product Title
                                try:
                                    prod_name = \
                                        prod.xpath('td[2]/a')[0].text.strip()
                                except IndexError:
                                    try:
                                        prod_name = \
                                            prod.xpath('td[2]/img')[-1]\
                                            .tail.strip()
                                    except IndexError:
                                        prod_name = \
                                            prod.xpath('td[2]')[0].text.strip()
                                    except AttributeError:
                                        continue
                                except AttributeError:
                                    continue

                                # if name is empty, ignore part
                                if not prod_name:
                                    continue

                                # Check if the previous part is replaced
                                if prod_name == 'Replaced by:':
                                    last_replaced = product
                                    continue

                                # Get Part Number
                                try:
                                    part_number = prod.xpath('td[3]/a')[0].text
                                    if not part_number:
                                        continue
                                except IndexError:
                                    continue

                                # Get Availability
                                try:
                                    available = prod.xpath('td[5]')[0] \
                                        .text.strip() != 'Out of production'
                                except IndexError:
                                    continue

                            except TypeError:
                                continue

                            product = {
                                'product': prod_name.strip(),
                                'part_number': part_number.strip(),
                                'diagram_number': diagram_number.strip(),
                                'replacements': [],
                                'is_available': available,
                            }

                            # we add replacements only in the replacement
                            # list of the replaced object to avoid
                            # duplicated inserts in DB
                            if last_replaced is None:
                                component['products'].append(product)
                            else:
                                last_replaced['replacements'].append(product)

                    # Save component
                    if section != {} and component['products'] != []:
                        section['sub_category'].append(component)


            # Save Last Section
            if section != {}:
                model['sub_category'].append(section)

            if model['sub_category']:
                category['sub_category'] = [model]

                print("\n'%s' done...\n" % mod_name)
                output_file_path = output_root_path + \
                    cat_slug + '/' + mod_slug[0:64] + \
                    '.json'
                create_output_file(catalog, output_file_path)

    print('Finished Marine Parts Europe Volvo Penta Scrapping...')

def threaded_volvo_scrapper(num_threads=1):
    from threading import Thread

    num_cats = 42

    if num_threads > num_cats:
        diff = 1
    else:
        diff = num_cats / num_threads

    threads = []
    for idx in range(0, num_cats, diff):
        t = Thread(target=marinepartseurope_volvo_penta_scrapper, args=(idx, idx+diff,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

##################################################################
# MARINE ENGINE WEB ##############################################
##################################################################


def marineengine_mercury_scrapper():
    """Scrapper for Marine Engine Mercury Parts."""
    global MARINE_ENGINE_BASE_URL, FILE_DIR

    images_root_folder = 'img/marine_engine/mercury/'

    print('Starting Marine Engine Mercury Scrapping...')
    # Categorys scraping
    page = request_get(
        MARINE_ENGINE_BASE_URL + '/parts/mercury-outboard/index.php'
    )
    tree = html.fromstring(page.content)
    # The selectors goes here so they dont recreate on every cicle
    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/a"
    xcategory_selector = "/html/body/main/div[2]/ul//li/a"
    # Change depending of the category to scrap
    xcomponents_selector = "/html/body/main/div[2]/div[1]/ul//li/a"
    ximg_selector = "/html/body/main/div[2]/p[1]/img"
    xproduct_selector = "/html/body/main/table//tr"
    xproduct_details_selector = ("/html/body/main/div[1]/div[1]"
                                 "/div[1]/div[2]/table//tr/td/p")
    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    for cat in tree.xpath(xpath_selector):
        cat_name = cat.text
        cat_slug = slugify(cat_name)

        category = {
            'category_name': 'category',
            'category': cat_name,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        # The navigation changes depending on the category selected
        if cat_name == 'Mercury Outboard (1960-present)':
            xcomponents_selector = "/html/body/main/div[2]/div[2]/ul//li/a"

        # Horse Power scraping
        page = request_get(
            MARINE_ENGINE_BASE_URL + category['category_url']
        )
        tree = html.fromstring(page.content)

        hps = tree.xpath(xcategory_selector)[INIT_OFFSET:]
        num_hps = len(hps) + INIT_OFFSET

        for idx, hp in enumerate(hps):
            hp_name = re.sub(r'[\n\t]+', '', hp.text)
            hp_slug = slugify(hp_name)
            print("'%s' starting... (%d of %d categories... %.2f %%)\n" %
                  (hp_name,
                   INIT_OFFSET + idx,
                   num_hps,
                   float(INIT_OFFSET + idx) / float(num_hps) * 100))
            horse_power = {
                'category_name': 'horse power',
                'category': hp_name,
                'category_url': hp.get('href'),
                'sub_category': []
            }

            category['sub_category'] = [horse_power]

            # Serial Range scrapping
            page = request_get(
                MARINE_ENGINE_BASE_URL + horse_power['category_url']
            )
            tree = html.fromstring(page.content)

            for srange in tree.xpath(xcategory_selector):
                srange_name = re.sub(r'[\n\t]+', '', srange.text)
                srange_slug = slugify(srange_name)
                serial_range = {
                    'category_name': 'serial_range',
                    'category': srange_name,
                    'category_url': srange.get('href'),
                    'sub_category': []
                }
                horse_power['sub_category'].append(serial_range)

                # Component scraping
                page = request_get(
                    MARINE_ENGINE_BASE_URL + serial_range['category_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcomponents_selector):
                    comp_name = comp.text
                    comp_slug = slugify(comp_name)
                    component = {
                        'category_name': 'component',
                        'category': comp_name,
                        'category_url': comp.get('href'),
                        'products': []
                    }

                    print("Scrapping component '%s' \n\turl: %s"
                          % (comp_name, component['category_url']))

                    serial_range['sub_category'].append(component)

                    # Products scrapping
                    page = request_get(
                        MARINE_ENGINE_BASE_URL + component['category_url']
                    )
                    tree = html.fromstring(page.content)

                    # Download Component Image
                    component_image = None
                    if(len(tree.xpath(ximg_selector)) > 0):
                        component_image = tree.xpath(ximg_selector)[0] \
                            .get('src')

                    if component_image:
                        r = request_get(component_image, stream=True)
                        image_rel_path = images_root_folder + \
                            hp_slug + '/' + \
                            srange_slug + '/' + \
                            comp_slug + '.gif'
                        image_final_path = os.path.join(FILE_DIR,
                                                        image_rel_path)
                        save_downloaded_file(image_final_path, r)
                        component_image = image_rel_path

                    component['image'] = component_image

                    # products cycle
                    diag_number = -1
                    product = None
                    last_replaced = None
                    for prod in tree.xpath(xproduct_selector):
                        if prod.get('class') is None:
                            try:
                                title = prod.xpath('td[3]/a/strong')[0].text
                            except IndexError:
                                title = prod.xpath('td[3]/p/strong/a')[0].text

                            try:
                                url = prod.xpath('td[3]/a')[0].get('href')
                            except IndexError:
                                url = prod.xpath('td[3]/p/strong/a')[0] \
                                    .get('href')

                            # Ignore parts with no title
                            if not title:
                                continue

                            title = re.sub(r' +', ' ', title.strip())

                            # Get original vs aftermarket attribute
                            origin = None
                            try:
                                origin = \
                                    prod.xpath('td[2]/p[2]/a/img')[0] \
                                    .get('src').split("/")[-1]
                                if origin == 'oem.png':
                                    origin = 'original'
                                elif origin == 'aftermarket.png':
                                    origin = 'aftermarket'
                            except IndexError:
                                pass

                            # Check if it's unavailable obsolete and replaced
                            is_replaced = False
                            if prod.xpath('td[3]/small[1]'):
                                is_available = False
                                xpath = prod.xpath('td[3]/small[2]/br')
                                if xpath is not None and xpath != []:
                                    match = xpath[0].tail.strip()
                                    is_replaced = "Replaced" in match
                            else:
                                is_available = True

                            # Product details scraping
                            page = request_get(
                                MARINE_ENGINE_BASE_URL + url
                            )
                            tree = html.fromstring(page.content)

                            count = 0
                            # Price and other details from the product page
                            for details in tree.xpath(
                                    xproduct_details_selector)[2:]:
                                value = (etree.tostring(details)
                                         .decode('utf-8')
                                         .replace('\n', '')
                                         .replace('\t', '')
                                         .replace('</p>', '')
                                         .replace('<strong>', '')
                                         .replace('</strong>', '')
                                         .replace('<p>', '')
                                         .split('<br/>')[1]
                                         .replace('&#8212;', '')
                                         .replace('&#160;', ' '))

                                if value:
                                    if count == 0:
                                        part_number = value.strip()
                                    else:
                                        manufacturer = value.strip()
                                        break

                                count += 1

                            title = get_product_title(title, part_number)
                            product = {
                                'diagram_number': diag_number,
                                'manufacturer': manufacturer,
                                'origin': origin,
                                'part_number': part_number,
                                'product': title,
                                'is_available': is_available,
                                'replacements': []
                            }

                            # we add replacements only in the replacement
                            # list of the replaced object to avoid
                            # duplicates inserts in DB
                            if last_replaced is None:
                                component['products'].append(product)
                            else:
                                last_replaced['replacements'].append(product)

                            if is_replaced:
                                last_replaced = product

                        else:
                            product = None
                            last_replaced = None
                            diag_number = prod.xpath("td[1]/span/strong")[0] \
                                .text.replace('#', '')

            print("\n'%s' done...\n" % hp_name)
            output_file_path = FILE_DIR + '/marine_engine/mercury/' + \
                cat_slug + '/' + hp_slug + \
                '.json'
            create_output_file(catalog, output_file_path)


def marineengine_johnson_evinrude_scrapper(begin=0, end=None):
    """Scrapper for Marine Engine Johnson Evinrude Parts."""
    # Marineengine base url
    global INIT_OFFSET, INIT_OFFSET_2, MARINE_ENGINE_BASE_URL, FILE_DIR

    images_root_folder = 'img/marine_engine/j&e/'

    print('Starting Marine Engine Johnson & Evinrude Scrapping...')
    # Categorys scraping
    page = request_get(
        MARINE_ENGINE_BASE_URL + '/parts/parts.php'
    )
    tree = html.fromstring(page.content)

    xpath_selector = ("/html/body/main/div[1]/div[2]/div[1]/div[2]"
                      "/div/ul//li/h3/a")
    xyears_selector = "/html/body/main/div[2]/table/tr[1]/td[1]/ul//li/a"
    # xmanuals_selector = \
    #   "/html/body/main/div[2]/table/tr/td/div[1]/div[1]/ul//li/a"
    xcomponents_selector = ("/html/body/main/div[2]/table/tr/td/div[1]"
                            "/div[2]/ul//li/a")
    # xmanual_img_selector = "/html/body/main/div/div[1]/img"
    # xmanual_details_selector = "/html/body/main/div/div[2]/table//tr"
    xcomponent_parts_selector = "/html/body/main//div/table//tr"
    xcomponent_img_selector = "/html/body/main/div[2]/div/p[1]/img"
    xproduct_details_selector = ("/html/body/main/div[1]/div[1]/div[1]"
                                 "/div[2]/table//tr/td/p")
    # xproduct_img_selector = ("/html/body/main/div[1]/div[1]/div[1]/div[1]"
    #                         "/table/tr/td/a/img")

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    # Categories on johnson evinrude
    for cat in tree.xpath(xpath_selector)[0:1]:
        cat_name = cat.text
        cat_slug = slugify(cat_name)

        category = {
            'category_name': 'category',
            'category': cat_name,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        # Years cycle
        page = request_get(
            MARINE_ENGINE_BASE_URL + category['category_url']
        )
        tree = html.fromstring(page.content)

        # Apply given offset in years cycle
        yrs = tree.xpath(xyears_selector)[begin:end]
        num_yrs = len(yrs) + begin

        for idx, yr in enumerate(yrs):
            yr_name = re.sub(r'[\n\t]+', '', yr.text)
            yr_slug = slugify(yr_name)
            print("'%s' starting... (%d of %d categories... %.2f %%)\n" %
                  (yr_name,
                   begin + idx,
                   num_yrs,
                   float(begin + idx) / float(num_yrs) * 100))
            year = {
                'category_name': 'years',
                'category': yr_name,
                'category_url': yr.get('href'),
                'sub_category': []
            }
            category['sub_category'] = [year]

            page = request_get(
                MARINE_ENGINE_BASE_URL + year['category_url']
            )
            tree = html.fromstring(page.content)

            # Apply given offset in horse power cycle
            hps = tree.xpath(xyears_selector)[INIT_OFFSET_2:]

            # Reset offset so it can only be applied once
            INIT_OFFSET_2 = 0

            # Horse power cycle
            for hp in hps:
                hp_name = re.sub(r'[\n\t]+', '', hp.text)
                hp_slug = slugify(hp_name)
                hp_link = hp.get('href')

                print("\n\tScrapping Horse Power '%s'\n\t\turl: %s\n"
                      % (hp_name, hp_link))

                horse_power = {
                    'category_name': 'horse power',
                    'category': hp_name,
                    'category_url': hp_link,
                    'sub_category': []
                }
                year['sub_category'] = [horse_power]

                page = request_get(
                    MARINE_ENGINE_BASE_URL + horse_power['category_url']
                )
                tree = html.fromstring(page.content)

                # Models cycle
                for model in tree.xpath(xyears_selector):
                    model_name = re.sub(r'[\n\t]+', '', model.text) \
                        .lstrip("Model ").strip()
                    model_slug = slugify(model_name)

                    model = {
                        'category_name': 'model',
                        'category': model_name,
                        'category_url': model.get('href'),
                        'sub_category': []
                    }

                    horse_power['sub_category'].append(model)

                    page = request_get(
                        MARINE_ENGINE_BASE_URL + model['category_url']
                    )
                    tree = html.fromstring(page.content)

                    # Parts cycle
                    for comp in tree.xpath(xcomponents_selector):
                        comp_name = comp.text
                        comp_slug = slugify(comp_name)
                        component = {
                            'category_name': 'component',
                            'category': comp_name,
                            'category_url': comp.get('href'),
                            'products': []
                        }

                        # print("\t\tScrapping component '%s' from model '%s'\n"
                        #       "\t\t\turl: %s"
                        #       % (comp_name,
                        #          model_name,
                        #          component['category_url']))

                        page = request_get(
                            MARINE_ENGINE_BASE_URL + component['category_url']
                        )
                        tree = html.fromstring(page.content)

                        # Download Component Image
                        component_image = None
                        if(len(tree.xpath(xcomponent_img_selector)) > 0):
                            component_image = \
                                MARINE_ENGINE_BASE_URL + \
                                tree.xpath(xcomponent_img_selector)[0] \
                                .get('src')

                        if component_image:
                            r = request_get(component_image, stream=True)
                            image_rel_path = images_root_folder + \
                                yr_slug + '/' + \
                                hp_slug + '/' + \
                                model_slug + '/' + \
                                comp_slug + '.gif'
                            image_final_path = os.path.join(FILE_DIR,
                                                            image_rel_path)
                            save_downloaded_file(image_final_path, r)
                            component_image = image_rel_path

                        component['image'] = component_image

                        # parts cycle
                        diag_number = -1
                        product = None
                        last_replaced = None
                        for prod in tree.xpath(xcomponent_parts_selector):
                            if prod.get('class') is None:
                                title = ''
                                link = ''

                                if prod.xpath('td[3]/a/strong'):
                                    title = \
                                        re.sub(' +',
                                               ' ',
                                               prod.xpath('td[3]/a/strong')[0]
                                               .text or '')
                                    link = prod.xpath('td[3]/a')[0].get('href')
                                elif prod.xpath('td[3]/p/strong/a'):
                                    title = \
                                        re.sub(
                                            ' +',
                                            ' ',
                                            prod.xpath('td[3]/p/strong/a')[0]
                                            .text or '')
                                    link = prod.xpath('td[3]/p/strong/a')[0] \
                                        .get('href')

                                if title and link:
                                    title = re.sub(r' +', ' ', title.strip())

                                    # Get original vs aftermarket attribute
                                    origin = None
                                    try:
                                        origin = \
                                            prod.xpath('td[2]/p[2]/a/img')[0] \
                                            .get('src').split("/")[-1]
                                        if origin == 'oem.png':
                                            origin = 'original'
                                        elif origin == 'aftermarket.png':
                                            origin = 'aftermarket'
                                    except IndexError:
                                        pass

                                    # Check if it's unavailable obsolete and
                                    # replaced
                                    is_replaced = False
                                    if prod.xpath('td[3]/small[1]'):
                                        is_available = False
                                        xpath = prod.xpath('td[3]/small[2]/br')
                                        if xpath is not None and xpath != []:
                                            match = xpath[0].tail.strip()
                                            is_replaced = "Replaced" in match
                                    else:
                                        is_available = True

                                    # Get price
                                    price = None
                                    if is_available:
                                        elem = \
                                            prod.xpath('td[3]/p[2]/small/span')
                                        if elem:
                                            price = \
                                                elem[-1].text.lstrip('$')\
                                                .rstrip()

                                    page = request_get(
                                        MARINE_ENGINE_BASE_URL +
                                        link
                                    )
                                    tree = html.fromstring(page.content)

                                    count = 0
                                    # Price and other details from the
                                    # product page
                                    for details in tree \
                                            .xpath(
                                                xproduct_details_selector)[2:]:
                                        value = \
                                            (etree.tostring(details)
                                                .decode('utf-8')
                                                .replace('\n', '')
                                                .replace('\t', '')
                                                .replace('</p>', '')
                                                .replace('<strong>', '')
                                                .replace('</strong>', '')
                                                .replace('<p>', '')
                                                .split('<br/>')[1]
                                                .replace('&#8212;', '')
                                                .replace('&#160;', ' '))

                                        if value:
                                            if count == 0:
                                                part_number = \
                                                    value.strip().split()[0]
                                            else:
                                                manufacturer = \
                                                    value.strip()
                                                break

                                        count += 1

                                    title = \
                                        get_product_title(title, part_number)
                                    product = {
                                        'diagram_number': diag_number,
                                        'manufacturer': manufacturer,
                                        'origin': origin,
                                        'part_number': part_number,
                                        'price': price,
                                        'product': title,
                                        'is_available': is_available,
                                        'replacements': []
                                    }

                                    # we add replacements only in the
                                    # replacement list of the replaced
                                    # object to avoid duplicates inserts in DB
                                    if last_replaced is None:
                                        component['products'].append(product)
                                    else:
                                        last_replaced['replacements'] \
                                            .append(product)

                                    if is_replaced:
                                        last_replaced = product

                            else:
                                product = None
                                last_replaced = None
                                if prod.xpath('td/span/strong'):
                                    diag_number = \
                                        prod.xpath("td/span/strong")[0] \
                                            .text.strip().replace('#', '')

                        # Store the component
                        if component['products']:
                            model['sub_category'].append(component)

                print("\n'%s' done...\n" % yr.text)
                output_file_path = FILE_DIR + '/marine_engine/j&e/' + \
                    cat_slug + "/" + \
                    yr_slug + '-' + \
                    hp_slug + \
                    '.json'
                create_output_file(catalog, output_file_path)


def threaded_johnson_evinrude_scrapper(num_threads=1):
    from threading import Thread

    num_cats = 58

    if num_threads > num_cats:
        diff = 1
    else:
        diff = num_cats / num_threads

    threads = []
    for idx in range(0, num_cats, diff):
        t = Thread(target=marineengine_johnson_evinrude_scrapper, args=(idx, idx+diff,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

def marineengine_mercruiser_scrapper():
    """Scrapper for marine engine's Mercruiser section."""
    # Marineengine base url
    global MARINE_ENGINE_BASE_URL, FILE_DIR

    images_root_folder = 'img/marine_engine/mercruiser/'

    print('Starting Marine Engine Mercruiser Scrapping...')
    # Categorys scraping
    page = request_get(
        MARINE_ENGINE_BASE_URL + '/parts/mercruiser-stern-drive/index.php'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/a"
    xmodel_selector = "/html/body/main/div[2]/ul//li/a"
    xserial_range_selector = "/html/body/main/div[2]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/div[2]/ul//li/a"
    xcomponents_selector2 = "/html/body/main/div[2]/div/ul//li/a"
    xcomponent_img_selector = "/html/body/main/div[2]/p[1]/img"
    xcomponent_parts_selector = "/html/body/main/table//tr"
    xproduct_details_selector = ("/html/body/main/div[1]/div[1]/div[1]/div[2]/"
                                 "table//tr/td/p")

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    # Categories on mercruiser scrapper
    for cat in tree.xpath(xpath_selector):
        cat_name = cat.text
        cat_slug = slugify(cat_name)

        category = {
            'category_name': 'category',
            'category': cat_name,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        page = request_get(
            MARINE_ENGINE_BASE_URL + category['category_url']
        )
        tree = html.fromstring(page.content)

        mods = tree.xpath(xmodel_selector)[INIT_OFFSET:]
        num_mods = len(mods) + INIT_OFFSET

        for idx, mod in enumerate(mods):
            mod_name = re.sub(r'[\n\t]+', '', mod.text)
            mod_slug = slugify(mod_name)
            print("'%s' starting... (%d of %d categories... %.2f %%)\n" %
                  (mod_name,
                   INIT_OFFSET + idx,
                   num_mods,
                   float(INIT_OFFSET + idx) / float(num_mods) * 100))
            model = {
                'category_name': 'model',
                'category': mod_name,
                'category_url': mod.get('href'),
                'sub_category': []
            }
            category['sub_category'] = [model]

            # Serial Range scrapping
            page = request_get(
                MARINE_ENGINE_BASE_URL + model['category_url']
            )
            tree = html.fromstring(page.content)

            for srange in tree.xpath(xserial_range_selector):
                srange_name = re.sub(r'[\n\t]+', '', srange.text)
                srange_slug = slugify(srange_name)
                serial_range = {
                    'category_name': 'serial_range',
                    'category': srange_name,
                    'category_url': srange.get('href'),
                    'sub_category': []
                }
                model['sub_category'].append(serial_range)

                # Component scraping
                page = request_get(
                    MARINE_ENGINE_BASE_URL + serial_range['category_url']
                )
                tree = html.fromstring(page.content)

                comps = []
                if tree.xpath(xcomponents_selector):
                    comps = tree.xpath(xcomponents_selector)
                elif tree.xpath(xcomponents_selector2):
                    comps = tree.xpath(xcomponents_selector2)
                else:
                    print("Caso especial mercruiser")

                for comp in comps:
                    comp_name = comp.text
                    comp_slug = slugify(comp_name)
                    component = {
                        'category_name': 'component',
                        'category': comp_name,
                        'category_url': comp.get('href'),
                        'products': []
                    }

                    print("Scrapping component '%s' \n\turl: %s"
                          % (component['category'], component['category_url']))

                    serial_range['sub_category'].append(component)

                    # Products scrapping
                    page = request_get(
                        MARINE_ENGINE_BASE_URL + component['category_url']
                    )
                    tree = html.fromstring(page.content)

                    component_image = None
                    if(len(tree.xpath(xcomponent_img_selector)) > 0):
                        component_image = \
                            tree.xpath(xcomponent_img_selector)[0].get('src')

                    if component_image:
                        r = request_get(component_image, stream=True)
                        image_rel_path = images_root_folder + \
                            mod_slug + '/' + \
                            srange_slug + '/' + \
                            comp_slug + '.gif'
                        image_final_path = os.path.join(FILE_DIR,
                                                        image_rel_path)
                        save_downloaded_file(image_final_path, r)
                        component_image = image_rel_path

                    component['image'] = component_image

                    diag_number = -1
                    product = None
                    last_replaced = None
                    # products cycle
                    for prod in tree.xpath(xcomponent_parts_selector):
                        if prod.get('class') is None:
                            try:
                                title = prod.xpath('td[3]/a/strong')[0].text
                                url = prod.xpath('td[3]/a')[0].get('href')
                            except IndexError:
                                title = prod.xpath('td[3]/p/strong/a')[0].text
                                url = prod.xpath('td[3]/p/strong/a')[0] \
                                    .get('href')
                            except TypeError:
                                continue

                            if title and url:

                                title = re.sub(r' +', ' ', title.strip())

                                # Get original vs aftermarket attribute
                                origin = None
                                try:
                                    origin = \
                                        prod.xpath('td[2]/p[2]/a/img')[0] \
                                        .get('src').split("/")[-1]
                                    if origin == 'oem.png':
                                        origin = 'original'
                                    elif origin == 'aftermarket.png':
                                        origin = 'aftermarket'
                                except IndexError:
                                    pass

                                # Check if it's unavailable obsolete and
                                # replaced
                                is_replaced = False
                                if prod.xpath('td[3]/small[1]'):
                                    is_available = False
                                    xpath = prod.xpath('td[3]/small[2]/br')
                                    if xpath is not None and xpath != []:
                                        match = xpath[0].tail.strip()
                                        is_replaced = "Replaced" in match
                                else:
                                    is_available = True

                                # Product details scraping
                                page = request_get(
                                    MARINE_ENGINE_BASE_URL +
                                    url
                                )
                                tree = html.fromstring(page.content)

                                count = 0
                                # Price and other details from the product page
                                for details in tree.xpath(
                                        xproduct_details_selector)[2:]:
                                    value = (etree.tostring(details)
                                             .decode('utf-8')
                                             .replace('\n', '')
                                             .replace('\t', '')
                                             .replace('</p>', '')
                                             .replace('<strong>', '')
                                             .replace('</strong>', '')
                                             .replace('<p>', '')
                                             .split('<br/>')[1]
                                             .replace('&#8212;', '')
                                             .replace('&#160;', ' '))

                                    if value:
                                        if count == 0:
                                            part_number = value.strip()
                                        else:
                                            manufacturer = value.strip()
                                            break

                                    count += 1

                                title = get_product_title(title, part_number)
                                product = {
                                    'diagram_number': diag_number,
                                    'manufacturer': manufacturer,
                                    'origin': origin,
                                    'part_number': part_number,
                                    'product': title,
                                    'is_available': is_available,
                                    'replacements': []
                                }

                                # we add replacements only in the replacement
                                # list of the replaced object to avoid
                                # duplicates inserts in DB
                                if last_replaced is None:
                                    component['products'].append(product)
                                else:
                                    last_replaced['replacements']\
                                        .append(product)

                                if is_replaced:
                                    last_replaced = product

                        else:
                            product = None
                            last_replaced = None
                            if prod.xpath('td/span/strong'):
                                diag_number = prod.xpath("td/span/strong")[0] \
                                    .text.replace('#', '').strip()

            print("\n'%s' done...\n" % mod_name)
            output_file_path = FILE_DIR + '/marine_engine/mercruiser/' + \
                cat_slug + '/' + mod_slug + \
                '.json'
            create_output_file(catalog, output_file_path)


def marineengine_force_scrapper():
    # Marineengine base url
    MARINE_ENGINE_BASE_URL = 'https://www.marineengine.com'
    # Categorys scraping
    page = request_get(
        base_url + '/parts/force-outboard-parts/'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "/html/body/main/div[2]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/div[2]/ul//li/a"
    xcomponents_selector2 = "/html/body/main/div[2]/div/ul//li/a"
    xcomponent_img_selector = "/html/body/main/div[2]/p[1]/img"
    xcomponent_parts_selector = "/html/body/main/table//tr"
    xproduct_details_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/table//tr/td/p"
    xproduct_unavailable_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/div/a"
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/table/tr/td/a/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    # Categorys on Force scrapper
    for hp in tree.xpath(xpath_selector):
        horse_power = {
            'category_name': 'horse power',
            'category': hp.text.replace('\n', '').replace('\t', ''),
            'category_url': hp.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(horse_power)

        page = requests.get(
            base_url + horse_power['category_url']
        )
        tree = html.fromstring(page.content)
        # Years cycle
        for sr in tree.xpath(xpath_selector):
            serial_range = {
                'category_name': 'serial range',
                'category': sr.text.replace('\n', '').replace('\t',''),
                'category_url': sr.get('href'),
                'sub_category': []
            }
            horse_power['sub_category'].append(serial_range)

            page = requests.get(
                base_url + serial_range['category_url']
            )
            tree = html.fromstring(page.content)

            comps = []
            if tree.xpath(xcomponents_selector):
                comps = tree.xpath(xcomponents_selector)
            elif tree.xpath(xcomponents_selector2):
                comps = tree.xpath(xcomponents_selector2)
            else:
                print("CASO ESPECIAL force" + base_url + serial_range['category_url'])

            for comp in comps:
                component = {
                    'category_name': 'component',
                    'category': comp.text.replace('\n', '').replace('\t',''),
                    'category_url': comp.get('href'),
                    'products': []
                }
                serial_range['sub_category'].append(component)

                page = requests.get(
                    base_url + component['category_url']
                )
                tree = html.fromstring(page.content)

                component_image = None
                if(len(tree.xpath(xcomponent_img_selector)) > 0):
                    component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

                if component_image:
                    r = requests.get(component_image, stream=True)
                    save_downloaded_file('img/marine_engine/force/'+ component_image.split('/')[-1], r)
                    component_image = 'img/marine_engine/force/'+ component_image.split('/')[-1]

                component['image'] = component_image

                diag_number = -1
                product = None
                old_product = None
                recomended = None
                # products cycle
                for prod in tree.xpath(xcomponent_parts_selector):
                    if prod.get('class') is None:
                        name = ''
                        link = ''
                        if prod.xpath('td[3]/a/strong'):
                            name = re.sub(' +', ' ', prod.xpath('td[3]/a/strong')[0].text)
                            link = prod.xpath('td[3]/a')[0].get('href')
                        elif prod.xpath('td[3]/p/strong/a'):
                            name = re.sub(' +', ' ', prod.xpath('td[3]/p/strong/a')[0].text)
                            link = prod.xpath('td[3]/p/strong/a')[0].get('href')

                        if name and link:
                            product = {
                                'product': name,
                                'product_url': link,
                                'diagram_number': diag_number
                            }
                            component['products'].append(product)

                            page = requests.get(
                                base_url + product['product_url']
                            )
                            tree = html.fromstring(page.content)
                            prod_image = None

                            if(len(tree.xpath(xproduct_img_selector)) > 0):
                                prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

                            if prod_image and 'noimage' not in prod_image:
                                r = requests.get(base_url + prod_image, stream=True)
                                save_downloaded_file('img/marine_engine/force/'+ prod_image.split('/')[-1], r)
                                prod_image = 'img/marine_engine/force/'+ prod_image.split('/')[-1]
                            else:
                                prod_image = None

                            product['product_image'] = prod_image

                            if tree.xpath(xproduct_unavailable_selector):
                                recomended = tree.xpath(xproduct_unavailable_selector)[0].get('href').replace(' ', '20%')

                            # Assemble the product json object
                            product['recomended'] = recomended

                            count = 0
                            # Price and other details from the product page
                            for details in tree.xpath(xproduct_details_selector):
                                value = (etree.tostring(details).decode('utf-8').replace('\n', '').replace('\t', '')
                                        .replace('</p>', '').replace('<strong>', '').replace('</strong>', '')
                                        .replace('<p>', '').split('<br/>')[1].replace('&#8212;', '').replace('&#160;', ' '))

                                if value:
                                    if count == 0:
                                        product['list_price'] = value
                                    elif count == 1:
                                        product['your_price'] = value
                                    elif count == 2:
                                        product['part_number'] = value.split()[0]
                                    else:
                                        product['manufacturer'] = value

                                count += 1

                            if old_product:
                                old_product['recomended'] = product

                            old_product = product

                            counter += 1
                    else:
                        product = None
                        old_product = None
                        if prod.xpath('td/span/strong'):
                            diag_number = prod.xpath("td/span/strong")[0].text.replace('#','')

                    counter += 1

                    if counter > 100:
                        print('Finishing Marine Engine Force Scraping...\n')
                        catalog['scraping_successful'] = True
                        with open('marine_engine_force-' + scrap_date + '.json', 'w') as outfile:
                            json.dump(catalog, outfile, indent=4)
                            pass
                        return


def marineengine_mariner_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'

    xpath_selector = "/html/body/main/div[2]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/div[2]/ul//li/a"
    xcomponents_selector2 = "/html/body/main/div[2]/div/ul//li/a"
    xcomponent_img_selector = "/html/body/main/div[2]/p[1]/img"
    xcomponent_parts_selector = "/html/body/main/table//tr"
    xproduct_details_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/table//tr/td/p"
    xproduct_unavailable_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/div/a"
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/table/tr/td/a/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    count = 0
    cats = ['Mariner Outboard', 'Mariner Racing Outboard']
    for url in ['/parts/mariner-outboard-parts/', '/parts/mercury-racing-outboard-parts/']:
        category = {
            'category_name': 'category',
            'category': cats[count],
            'category_url': url,
            'sub_category': []
        }
        catalog['categories'].append(category)
        count += 1
        # Categorys scraping
        page = requests.get(
            base_url + url
        )
        tree = html.fromstring(page.content)

        # Categorys on marine
        for hp in tree.xpath(xpath_selector):
            horse_power = {
                'category_name': 'horse power',
                'category': hp.text.replace('\n', '').replace('\t',''),
                'category_url': hp.get('href'),
                'sub_category': []
            }
            category['sub_category'].append(horse_power)

            page = requests.get(
                base_url + horse_power['category_url']
            )
            tree = html.fromstring(page.content)
            # Years cycle
            for sr in tree.xpath(xpath_selector):
                serial_range = {
                    'category_name': 'serial range',
                    'category': sr.text.replace('\n', '').replace('\t',''),
                    'category_url': sr.get('href'),
                    'sub_category': []
                }
                horse_power['sub_category'].append(serial_range)

                page = requests.get(
                    base_url + serial_range['category_url']
                )
                tree = html.fromstring(page.content)

                comps = []
                if tree.xpath(xcomponents_selector):
                    comps = tree.xpath(xcomponents_selector)
                elif tree.xpath(xcomponents_selector2):
                    comps = tree.xpath(xcomponents_selector2)
                else:
                    print("Caso Especial mariner")

                for comp in comps:
                    component = {
                        'category_name': 'component',
                        'category': comp.text.replace('\n', '').replace('\t',''),
                        'category_url': comp.get('href'),
                        'products': []
                    }
                    serial_range['sub_category'].append(component)

                    page = requests.get(
                        base_url + component['category_url']
                    )
                    tree = html.fromstring(page.content)

                    component_image = None
                    if(len(tree.xpath(xcomponent_img_selector)) > 0):
                        component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

                    if component_image:
                        r = requests.get(component_image, stream=True)
                        save_downloaded_file('img/marine_engine/mariner/'+ component_image.split('/')[-1], r)
                        component_image = 'img/marine_engine/mariner/'+ component_image.split('/')[-1]

                    component['image'] = component_image

                    diag_number = -1
                    product = None
                    old_product = None
                    recomended = None
                    # products cycle
                    for prod in tree.xpath(xcomponent_parts_selector):
                        if prod.get('class') is None:
                            name = ''
                            link = ''
                            if prod.xpath('td[3]/a/strong'):
                                name = re.sub(' +', ' ', prod.xpath('td[3]/a/strong')[0].text)
                                link = prod.xpath('td[3]/a')[0].get('href')
                            elif prod.xpath('td[3]/p/strong/a'):
                                name = re.sub(' +', ' ', prod.xpath('td[3]/p/strong/a')[0].text)
                                link = prod.xpath('td[3]/p/strong/a')[0].get('href')

                            if name and link:
                                product = {
                                    'product': name,
                                    'product_url': link,
                                    'diagram_number': diag_number
                                }
                                component['products'].append(product)

                                page = requests.get(
                                    base_url + product['product_url']
                                )
                                tree = html.fromstring(page.content)
                                prod_image = None

                                if(len(tree.xpath(xproduct_img_selector)) > 0):
                                    prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

                                if prod_image and 'noimage' not in prod_image:
                                    r = requests.get(base_url + prod_image, stream=True)
                                    save_downloaded_file('img/marine_engine/mariner/'+ prod_image.split('/')[-1], r)
                                    prod_image = 'img/marine_engine/mariner/'+ prod_image.split('/')[-1]
                                else:
                                    prod_image = None

                                product['product_image'] = prod_image

                                if tree.xpath(xproduct_unavailable_selector):
                                    recomended = tree.xpath(xproduct_unavailable_selector)[0].get('href').replace(' ', '20%')

                                # Assemble the product json object
                                product['recomended'] = recomended

                                count = 0
                                # Price and other details from the product page
                                for details in tree.xpath(xproduct_details_selector):
                                    value = (etree.tostring(details).decode('utf-8').replace('\n', '').replace('\t', '')
                                            .replace('</p>', '').replace('<strong>', '').replace('</strong>', '')
                                            .replace('<p>', '').split('<br/>')[1].replace('&#8212;', '').replace('&#160;', ' '))

                                    if value:
                                        if count == 0:
                                            product['list_price'] = value
                                        elif count == 1:
                                            product['your_price'] = value
                                        elif count == 2:
                                            product['part_number'] = value.split()[0]
                                        else:
                                            product['manufacturer'] = value

                                    count += 1

                                if old_product:
                                    old_product['recomended'] = product

                                old_product = product

                                counter += 1
                        else:
                            product = None
                            old_product = None
                            if prod.xpath('td/span/strong'):
                                diag_number = prod.xpath("td/span/strong")[0].text.replace('#','')

                        counter += 1

                        if counter > 100:
                            print('Finishing Marine Engine Mariner Scraping...\n')
                            catalog['scraping_successful'] = True
                            with open('marine_engine_mariner-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return


def marineengine_omc_sterndrive_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scraping
    page = requests.get(
        base_url + '/parts/omc-parts/omc-boat-parts.php'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "/html/body/main/div[2]/table/tr[1]/td[1]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/table/tr/td/div[1]/div[2]/ul//li/a"
    xcomponents_selector2 = "/html/body/main/div[2]/div/ul//li/a"
    xcomponent_img_selector = "/html/body/main/div[2]/div/p[1]/img"
    xcomponent_parts_selector = "/html/body/main//div/table//tr"
    xproduct_details_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/table//tr/td/p"
    xproduct_unavailable_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/div/a"
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/table/tr/td/a/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    for yr in tree.xpath(xpath_selector):
        year = {
            'category_name': 'year',
            'category': yr.text.replace('\n', '').replace('\t',''),
            'category_url': yr.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(year)

        page = requests.get(
            base_url + year['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xpath_selector):
            horse_power = {
                'category_name': 'horse power/ liters',
                'category': hp.text.replace('\n', '').replace('\t',''),
                'category_url': hp.get('href'),
                'sub_category': []
            }
            year['sub_category'].append(horse_power)

            page = requests.get(
                base_url + horse_power['category_url']
            )
            tree = html.fromstring(page.content)

            for md in tree.xpath(xpath_selector):
                model = {
                    'category_name': 'model',
                    'category': md.text.replace('\n', '').replace('\t',''),
                    'category_url': md.get('href'),
                    'sub_category': []
                }
                horse_power['sub_category'].append(model)

                page = requests.get(
                    base_url + model['category_url']
                )
                tree = html.fromstring(page.content)

                comps = []
                if tree.xpath(xcomponents_selector):
                    comps = tree.xpath(xcomponents_selector)
                elif tree.xpath(xcomponents_selector2):
                    comps = tree.xpath(xcomponents_selector2)
                else:
                    print("Caso Especial OMC")

                for comp in comps:
                    component = {
                        'category_name': 'component',
                        'category': comp.text.replace('\n', '').replace('\t',''),
                        'category_url': comp.get('href'),
                        'products': []
                    }
                    model['sub_category'].append(component)

                    page = requests.get(
                        base_url + component['category_url']
                    )
                    tree = html.fromstring(page.content)

                    component_image = None
                    if(len(tree.xpath(xcomponent_img_selector)) > 0):
                        component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

                    if component_image:
                        r = requests.get(base_url + component_image, stream=True)
                        save_downloaded_file('img/marine_engine/omc/'+ component_image.split('/')[-1], r)
                        component_image = 'img/marine_engine/omc/'+ component_image.split('/')[-1]

                    component['image'] = component_image

                    diag_number = -1
                    product = None
                    old_product = None
                    recomended = None
                    # products cycle
                    for prod in tree.xpath(xcomponent_parts_selector):
                        if prod.get('class') is None:
                            name = ''
                            link = ''
                            if prod.xpath('td[3]/a/strong'):
                                name = re.sub(' +', ' ', prod.xpath('td[3]/a/strong')[0].text)
                                link = prod.xpath('td[3]/a')[0].get('href')
                            elif prod.xpath('td[3]/p/strong/a'):
                                name = re.sub(' +', ' ', prod.xpath('td[3]/p/strong/a')[0].text)
                                link = prod.xpath('td[3]/p/strong/a')[0].get('href')

                            if name and link:
                                product = {
                                    'product': name,
                                    'product_url': link,
                                    'diagram_number': diag_number
                                }
                                component['products'].append(product)

                                page = requests.get(
                                    base_url + product['product_url']
                                )
                                tree = html.fromstring(page.content)
                                prod_image = None

                                if(len(tree.xpath(xproduct_img_selector)) > 0):
                                    prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

                                if prod_image and 'noimage' not in prod_image:
                                    r = requests.get(base_url + prod_image, stream=True)
                                    save_downloaded_file('img/marine_engine/omc/'+ prod_image.split('/')[-1], r)
                                    prod_image = 'img/marine_engine/omc/'+ prod_image.split('/')[-1]
                                else:
                                    prod_image = None

                                product['product_image'] = prod_image

                                if tree.xpath(xproduct_unavailable_selector):
                                    recomended = tree.xpath(xproduct_unavailable_selector)[0].get('href').replace(' ', '20%')

                                # Assemble the product json object
                                product['recomended'] = recomended

                                count = 0
                                # Price and other details from the product page
                                for details in tree.xpath(xproduct_details_selector):
                                    value = (etree.tostring(details).decode('utf-8').replace('\n', '').replace('\t', '')
                                            .replace('</p>', '').replace('<strong>', '').replace('</strong>', '')
                                            .replace('<p>', '').split('<br/>')[1].replace('&#8212;', '').replace('&#160;', ' '))

                                    if value:
                                        if count == 0:
                                            product['list_price'] = value
                                        elif count == 1:
                                            product['your_price'] = value
                                        elif count == 2:
                                            product['part_number'] = value.split()[0]
                                        else:
                                            product['manufacturer'] = value

                                    count += 1

                                if old_product:
                                    old_product['recomended'] = product

                                old_product = product

                                counter += 1
                        else:
                            product = None
                            old_product = None
                            if prod.xpath('td/span/strong'):
                                diag_number = prod.xpath("td/span/strong")[0].text.replace('#','')

                        counter += 1

                        if counter > 100:
                            print('Finishing Marine Engine OMC Sterndrive Scraping...\n')
                            catalog['scraping_successful'] = True
                            with open('marine_engine_omc_sterndrive-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return

########################################################
## MARINE PARTS EXPRESS WEB
########################################################
def marinepartsexpress_chrysler_marine_scrapper():
    base_url = 'http://www.marinepartsexpress.com/Chrysler_Schematics/'
    # Categorys scraping
    page = requests.get(
        base_url
    )
    tree = html.fromstring(page.content)

    xpath_selector = "/html/body/div//table/tr/td[2]/a[1]"
    xcomponents_selector = "/html/body/div//table[position()>1]//tr"
    xproduct_selector = "/html/body/div/table[2]/tr[position()>1]"
    xcomponent_img_selector = "/html/body/div/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    # Categorys on marine parts chrysler
    for item in tree.xpath(xpath_selector):
        models = []
        page = requests.get(
            base_url + item.get('href')
        )
        tree = html.fromstring(page.content)
        old_cat = ''

        for comp in tree.xpath(xcomponents_selector):
            # Means is a new component table
            if comp.xpath('td[1]/strong') and comp.xpath('td[1]/strong')[0].text:
                if "Components" in comp.xpath('td[1]/strong')[0].text:
                    if old_cat != comp.xpath('td[1]/strong')[0].text:
                        old_cat = comp.xpath('td[1]/strong')[0].text
                        category = {
                            'category_name': 'category',
                            'category': comp.xpath('td[1]/strong')[0].text,
                            'category_url': item.get('href'),
                            'sub_category': []
                        }
                        subcat = None
            elif comp.xpath('td[1]/strong/i'):
                if comp.xpath('td[1]/strong/i')[0].text:
                    subcat = {
                        'category_name': 'category',
                        'category': comp.xpath('td[1]/strong/i')[0].text,
                        'category_url': item.get('href'),
                        'sub_category': []
                    }
            else:
                for model in comp.xpath('td/a'):
                    component = {
                        'category_name': 'component',
                        'category': comp.xpath('td[1]')[0].text,
                        'category_url': model.get('href'),
                        'products': []
                    }

                    # Get Products for component
                    page = requests.get(
                        base_url + component['category_url']
                    )
                    tree2 = html.fromstring(page.content)

                    component_image = None
                    if(len(tree2.xpath(xcomponent_img_selector)) > 0):
                        component_image = tree2.xpath(xcomponent_img_selector)[0].get('src')

                    if component_image:
                        r = requests.get(base_url + component_image, stream=True)
                        save_downloaded_file('img/marine_express/chrysler/'+ component_image.split('/')[-1], r)
                        component_image = 'img/marine_express/chrysler/'+ component_image.split('/')[-1]

                    component['image'] = component_image

                    for prod in tree2.xpath(xproduct_selector):
                        if(prod.xpath('td')):
                            product = {
                                'product_url': component['category_url'],
                            }
                            component['products'].append(product)
                            if prod.xpath('td[2]'):
                                product['diagram_number'] = prod.xpath('td[1]')[0].text
                                product['product'] = prod.xpath('td[2]')[0].text
                                product['part_number'] = prod.xpath('td[3]')[0].text
                            else:
                                product['notes'] = prod.xpath('td[1]')[0].text

                    # Keep the component and tree structure
                    if model.text not in models:
                        models.append(model.text)
                        mod = {
                            'category_name': 'model',
                            'category': model.text,
                            'category_url': item.get('href'),
                            'sub_category': []
                        }
                        catalog['categories'].append(mod)
                    else:
                        for mod in catalog['categories']:
                            if mod['category'] == model.text:
                                break

                    present = False
                    for cat in mod['sub_category']:
                        if cat['category'] == category['category']:
                            present = True
                            break

                    if not present:
                        catcopy = copy.deepcopy(category)
                        mod['sub_category'].append(catcopy)
                        if subcat:
                            subpresent = False
                            for subc in category['sub_category']:
                                if subc['category'] == subcat['category']:
                                    subpresent = True
                                    break
                            if not subpresent:
                                subc = copy.deepcopy(subcat)
                                catcopy['sub_category'].append(subc)

                            catcopy = subc
                    else:
                        if subcat:
                            subpresent = False
                            for subc in cat['sub_category']:
                                if subc['category'] == subcat['category']:
                                    subpresent = True
                                    break

                            if not subpresent:
                                subc = copy.deepcopy(subcat)
                                cat['sub_category'].append(subc)

                            catcopy = subc
                        else:
                            catcopy = cat

                    catcopy['sub_category'].append(component)

            counter += 1
            if counter > 100:
                print('Finishing Marine Parts Express Chrysler Marine Scraping...\n')
                catalog['scraping_successful'] = True
                with open('marine_parts_express_chrysler_marine-' + scrap_date + '.json', 'w') as outfile:
                    json.dump(catalog, outfile, indent=4)
                    pass
                break


def marinepartsexpress_crusader_scrapper():
    base_url = 'http://www.marinepartsexpress.com/crusaderschem.html'
    man_url = 'http://www.marinepartsexpress.com/'
    # Categorys scraping
    page = requests.get(
        base_url
    )
    tree = html.fromstring(page.content)

    xpath_selector = ("/html/body/div/div[2]/div[1]/"
                      "section[1]/blockquote/ul//li/a")
    xpath_selector2 = "/html/body/div/div[2]/div[1]/section[1]/table//tr/td"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    # Categorys on johnson_evinrude
    for item in tree.xpath(xpath_selector2):
        manual = {
            'category_name': 'manual',
            'products': item.xpath('a')[0].text,
            'manual_url': item.xpath('a')[0].get('href'),
            'image': item.xpath('img')[0].get('src'),
        }
        catalog['categories'].append(manual)

        if manual['manual_url']:
            print(man_url + manual['manual_url'].replace(' ', '%20'))
            r = requests.get(man_url +
                             manual['manual_url'].replace(' ', '%20'),
                             stream=True)
            save_downloaded_file('manuals/marine_express/crusader/' +
                                 manual['manual_url'].split('/')[-1], r)
            manual['manual_url'] = 'manuals/marine_express/crusader/' + \
                                   manual['manual_url'].split('/')[-1]

    for item in tree.xpath(xpath_selector):
        present = False
        manual = {
            'category_name': 'manual',
            'products': item.text,
            'manual_url': item.get('href'),
            'image': None,
        }

        for man in catalog['categories']:
            if man['manual_url'] == manual['manual_url']:
                present = True
                break

        if not present:
            catalog['categories'].append(manual)
            if manual['manual_url']:
                print(man_url + manual['manual_url'].replace(' ', '%20'))
                r = requests.get(man_url + manual['manual_url']
                                 .replace(' ', '%20'),
                                 stream=True)
                save_downloaded_file(
                    'manuals/marine_express/crusader/' +
                    manual['manual_url'].split('/')[-1],
                    r)
                manual['manual_url'] = 'manuals/marine_express/crusader/' + \
                    manual['manual_url'].split('/')[-1]

    catalog['scraping_successful'] = True
    print('Finishing Marine Parts Express Crusader Manuals Scraping...\n')
    with open('marine_parts_express_crusader-' + scrap_date + '.json', 'w') \
            as outfile:
        json.dump(catalog, outfile, indent=4)
        pass


def marinepartsexpress_volvo_penta_marine_scrapper():
    """Scrapper for Marine Express's Volvo Parts."""
    global MARINE_EXPRESS_BASE_URL, FILE_DIR

    # Categorys scraping
    page = request_get(
        MARINE_EXPRESS_BASE_URL + '/VP_Schematics/directory.php'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "//*[@id='listing']//div/a"
    xmodel_selector = "//*[@id='listing']/div[position()>1]/a"
    xpdf_selector = "//*[@id='showpdf']//a"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    # Categorys on volvo
    for item in tree.xpath(xpath_selector):
        category = {
            'category_name': 'category',
            'category': item.xpath('strong')[0].text,
            'category_url': item.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        page = request_get(
            MARINE_EXPRESS_BASE_URL + category['category_url']
        )

        print(MARINE_EXPRESS_BASE_URL + category['category_url'] + " ACAA1")
        tree = html.fromstring(page.content)
        # models cycle
        for mod in tree.xpath(xmodel_selector):
            if not tree.xpath(xpdf_selector):
                model = {
                    'category_name': 'model',
                    'category': mod.xpath('strong')[0].text,
                    'category_url': mod.get('href'),
                    'sub_category': []
                }
                category['sub_category'].append(model)

                page = request_get(
                    MARINE_EXPRESS_BASE_URL + model['category_url']
                )
                tree = html.fromstring(page.content)
                print(MARINE_EXPRESS_BASE_URL +
                      model['category_url'] + " ACAA2")
                # components cycle
                for comp in tree.xpath(xmodel_selector):
                    if not tree.xpath(xpdf_selector):
                        component = {
                            'category_name': 'component',
                            'category': comp.xpath('strong')[0].text,
                            'category_url': comp.get('href'),
                            'sub_category': []
                        }
                        model['sub_category'].append(component)

                        page = request_get(
                            MARINE_EXPRESS_BASE_URL + component['category_url']
                        )
                        print(MARINE_EXPRESS_BASE_URL +
                              component['category_url'] + " ACA3")
                        tree2 = html.fromstring(page.content)
                        # Items cycle
                        if not tree2.xpath(xpdf_selector):
                            it = {
                                'category_name': 'item',
                                'category': item.xpath('strong')[0].text,
                                'category_url': item.get('href'),
                                'sub_category': []
                            }
                            component['sub_category'].append(component)
                            print("ANOTHER LEVEL NEEDED")
                        else:
                            print('pdf 1')
                            for man in tree2.xpath(xpdf_selector):
                                manual = {
                                    'category_name': 'manual',
                                    'products': man.xpath('strong')[0].text,
                                    'manual_url': man.get('href'),
                                    'image': None,
                                }
                                component['sub_category'].append(manual)

                                if manual['manual_url']:
                                    url = manual['manual_url'] \
                                        .replace("viewer.php?pdf=", "") \
                                        .split("&breadcrumb")[0]
                                    url = parse.unquote(url) \
                                        .replace('+', '%20')
                                    r = request_get(url, stream=True)
                                    save_downloaded_file(
                                        'manuals/marine_express/volvo/' +
                                        url.split('/')[-1], r)
                                    manual['manual_url'] = \
                                        'manuals/marine_express/volvo/' + \
                                        url.split('/')[-1]
                    else:
                        for man in tree.xpath(xpdf_selector):
                            print('pdf 2 ')
                            manual = {
                                'category_name': 'manual',
                                'products': man.xpath('strong')[0].text,
                                'manual_url': man.get('href'),
                                'image': None,
                            }
                            model['sub_category'].append(manual)

                            if manual['manual_url']:
                                url = manual['manual_url'] \
                                    .replace("viewer.php?pdf=", "") \
                                    .split("&breadcrumb")[0]
                                url = parse.unquote(url).replace('+', '%20')
                                print(url)
                                r = request_get(url, stream=True)
                                save_downloaded_file(
                                    'manuals/marine_express/volvo/' +
                                    url.split('/')[-1],
                                    r)
                                manual['manual_url'] = \
                                    'manuals/marine_express/volvo/' + \
                                    url.split('/')[-1]

                            counter += 1

                    if counter > 15:
                        catalog['scraping_successful'] = True
                        print("Finishing Marine Parts Express Volvo "
                              "Penta Marine Manuals Scraping...\n")
                        with open('marine_parts_express_volvo_penta_marine-' +
                                  scrap_date + '.json', 'w') as outfile:
                            json.dump(catalog, outfile, indent=4)
                            pass
                        return
            else:
                for man in tree.xpath(xpdf_selector):
                    manual = {
                        'category_name': 'manual',
                        'products': man.xpath('strong')[0].text,
                        'manual_url': man.get('href'),
                        'image': None,
                    }

                    present = False
                    for m in category['sub_category']:
                        if m['products'] == manual['products']:
                            present = True
                            break

                    if not present:
                        category['sub_category'].append(manual)

                        if manual['manual_url']:
                            url = manual['manual_url'] \
                                .replace("viewer.php?pdf=", "") \
                                .split("&breadcrumb")[0]
                            url = parse.unquote(url).replace('+', '%20')
                            print(url + " here")
                            r = request_get(url, stream=True)
                            save_downloaded_file(
                                'manuals/marine_express/volvo/' +
                                url.split('/')[-1],
                                r)
                            manual['manual_url'] = \
                                'manuals/marine_express/volvo/' + \
                                url.split('/')[-1]

                    model = {
                        'category_name': 'model',
                        'category': mod.xpath('strong')[0].text,
                        'category_url': mod.get('href'),
                        'sub_category': []
                    }
                    category['sub_category'].append(model)

                    page = request_get(
                        MARINE_EXPRESS_BASE_URL + model['category_url']
                    )
                    tree = html.fromstring(page.content)
                    print(MARINE_EXPRESS_BASE_URL +
                          model['category_url'] + " ACAA2")
                    # components cycle
                    for comp in tree.xpath(xmodel_selector):
                        if not tree.xpath(xpdf_selector):
                            component = {
                                'category_name': 'component',
                                'category': comp.xpath('strong')[0].text,
                                'category_url': comp.get('href'),
                                'sub_category': []
                            }
                            model['sub_category'].append(component)

                            page = request_get(
                                MARINE_EXPRESS_BASE_URL +
                                component['category_url']
                            )
                            print(MARINE_EXPRESS_BASE_URL +
                                  component['category_url'] + " ACA3")
                            tree2 = html.fromstring(page.content)
                            # Items cycle
                            if not tree2.xpath(xpdf_selector):
                                it = {
                                    'category_name': 'item',
                                    'category': item.xpath('strong')[0].text,
                                    'category_url': item.get('href'),
                                    'sub_category': []
                                }
                                component['sub_category'].append(component)
                                print("ANOTHER LEVEL NEEDED")
                            else:
                                print('pdf 1')
                                for man in tree2.xpath(xpdf_selector):
                                    manual = {
                                        'category_name': 'manual',
                                        'products': man.xpath('strong')[0]
                                        .text,
                                        'manual_url': man.get('href'),
                                        'image': None,
                                    }
                                    component['sub_category'].append(manual)

                                    if manual['manual_url']:
                                        url = manual['manual_url'] \
                                            .replace("viewer.php?pdf=", "") \
                                            .split("&breadcrumb")[0]
                                        url = parse.unquote(url) \
                                            .replace('+', '%20')
                                        r = request_get(url, stream=True)
                                        save_downloaded_file(
                                            'manuals/marine_express/volvo/' +
                                            url.split('/')[-1], r)
                                        manual['manual_url'] = \
                                            'manuals/marine_express/volvo/' + \
                                            url.split('/')[-1]

                    counter += 1


##################################################################
# BOATS NET
'''
Yamaha
http://www.boats.net/parts/search/Yamaha/Outboard/parts.html

Honda Marine
http://www.boats.net/parts/search/Honda/Outboard%20Engine/parts.html

Suzuki Marine
http://www.boats.net/parts/search/Suzuki/Outboard/parts.html
'''
##################################################################


def boatsnet_yamaha_scrapper(init_offset=0, end_offset=None):
    """Scrapper for Boatsnet's Yamaha Parts."""
    global BOATSNET_BASE_URL, FILE_DIR

    print('Starting Boatsnet\'s Yamaha Scrapping...')

    output_root_path = FILE_DIR + '/marine_europe/yamaha/'
    images_root_folder = 'img/boatsnet/yamaha/'

    # Categorys scraping
    page = request_get(BOATSNET_BASE_URL +
                        '/parts/search/Yamaha/Outboard/parts.html')
    tree = html.fromstring(page.content)

    xpath_selector = "//*[@class='year-link-container']/a"
    xhp_selector = "//*[@id='parts-surl-model']/div[position()>1]//div"
    xcomponents_selector = ("//*[@id='parts-surl-component']/"
                            "div[position()>1]/div/a")
    ximg_selector = "//*[@id='product-image']"
    xproduct_selector = "//*[@id='component-list']/div/div/div[2]/ul//li/div"
    xproduct_img_selector = ("//*[@id='main-product-image']/"
                             "div[2]/ul/li[1]/a/img")
    xproduct_img_selector2 = "//*[@id='main-product-image']/a/img"

    catalog = {
        'categories': [],
        'scraping_successful': False,
    }

    # Apply given offset in years cycle
    yrs = tree.xpath(xpath_selector)[init_offset:end_offset]

    # Categorys to scrap on boatsnet yamaha
    for yr in yrs:
        yr_name = yr.text
        yr_slug = slugify(yr_name)
        yr_url = yr.get('href')
        year = {
            'category_name': 'years',
            'category': yr_name,
            'category_url': yr_url,
            'sub_category': []
        }
        catalog['categories'] = [year]

        print("\n\tScrapping Year '%s'\n"
              % yr_name)

        # Horse Power scraping
        page = request_get(BOATSNET_BASE_URL +
                           yr_url)
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xhp_selector)[0:2]:
            if 'ResultHP' in hp.get('class'):
                hp_name = re.sub(r'[\n\t]+', '', hp.xpath('b')[0].text)
                hp_slug = slugify(hp_name)
                horse_power = {
                    'category_name': 'horse power',
                    'category': hp_name,
                    'sub_category': []
                }
                year['sub_category'].append(horse_power)

            elif 'result' in hp.get('class') and not hp.xpath('b'):
                model_name = re.sub(r'[\n\t]+', '', hp.xpath('a')[0].text)
                model_slug = slugify(model_name)
                model_url = hp.xpath('a')[0].get('href')
                model = {
                    'category_name': 'model',
                    'category': model_name,
                    'category_url': model_url,
                    'sub_category': []
                }
                horse_power['sub_category'].append(model)

                print("\n\tYear '%s'\n\t\tHorse Power '%s'\n"
                      "\t\t\tModel '%s'\n"
                      % (yr_name, hp_name, model_name))

                page = request_get(
                    BOATSNET_BASE_URL +
                    model['category_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcomponents_selector):
                    comp_name = comp.text
                    comp_slug = slugify(comp_name)
                    comp_url = comp.get('href')
                    component = {
                        'category_name': 'component',
                        'category': comp_name,
                        'category_url': comp_url,
                        'products': []
                    }
                    model['sub_category'].append(component)

                    # Products scraping
                    page = request_get(
                        BOATSNET_BASE_URL +
                        component['category_url']
                    )

                    tree = html.fromstring(page.content)
                    image = None
                    a = etree.tostring(tree.xpath('//*[@id="diagram"]')[0])
                    z = re.search(r"xlink:href\", *\"[^\"]*\"", a.decode()) \
                        .group(0).split(',')

                    if len(z) > 1:
                        image = re.sub(r'[\ \"]', '', z[1])
                        r = request_get('http:' + image, stream=True)
                        image_rel_path = images_root_folder + \
                            yr_slug + '/' + \
                            hp_slug + '/' + \
                            model_slug + '/' + \
                            comp_slug + '.gif'
                        image_final_path = os.path.join(FILE_DIR,
                                                        image_rel_path)
                        save_downloaded_file(image_final_path, r)
                        image = image_rel_path

                    component['image'] = image
                    count = 0
                    # old_diag = -1
                    product = None
                    # old_product = None
                    for prod in tree.xpath(xproduct_selector):
                        if 'ma-obs' in prod.get('class'):
                            product['is_available'] = False
                            count = -1
                        elif count == 0:
                            product = {
                                "diagram_number": re.sub(r'[\n\t]',
                                                         '',
                                                         prod.text.strip()),
                                'is_available': True,
                                'replacements': [],
                            }

                            """
                            if(old_diag == re.sub(r'[\n\t]', '', prod.text)):
                                product["recomended"] = old_product

                            old_product = product
                            old_diag = re.sub(r'[\n\t]', '', prod.text)
                            """
                            component['products'].append(product)
                        elif count == 1:
                            product['product'] = prod.xpath('h2/a')[0].text
                            product['product_url'] = prod.xpath('h2/a')[0] \
                                .get('href')
                            product['part_number'] = prod.xpath('p/a')[0].text
                        elif count == 2:
                            """
                            page = request_get(
                                BOATSNET_BASE_URL + product['product_url']
                            )
                            tree = html.fromstring(page.content)
                            image = None
                            if tree.xpath(xproduct_img_selector):
                                image = tree.xpath(xproduct_img_selector)[0] \
                                    .get('src')
                            elif tree.xpath(xproduct_img_selector2):
                                image = tree.xpath(xproduct_img_selector2)[0] \
                                    .get('src')


                            if image:
                                r = request_get('http:' + image, stream=True)
                                save_downloaded_file('img/boats_net/yamaha/' +
                                                     image.split('/')[-1],
                                                     r)
                                image = 'img/boats_net/yamaha/' + \
                                    image.split('/')[-1]
                            """

                            product['list_price'] = \
                                prod.xpath('div[1]')[0].text

                            # If theres another price
                            if prod.xpath('div[2]'):
                                product['price'] = \
                                    prod.xpath('div[2]')[0].text

                            product['manufacturer'] = "Yamaha"
                            product['image'] = image
                        elif count == 3:
                            count = -1

                        count += 1

        print("\n'%s' done...\n" % yr_name)
        output_file_path = FILE_DIR + '/boatsnet/yamaha/' + \
            yr_slug + '.json'
        create_output_file(catalog, output_file_path)


def boatsnet_honda_marine_scrapper():
    # Marineengine base url
    base_url = 'http://www.boats.net'
    # Categorys for scraping
    page = requests.get(
        base_url + '/parts/search/Honda/Outboard%20Engine/parts.html'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "//*[@class='year-link-container']/a"
    xhp_selector = "//*[@id='parts-surl-model']/div[position()>1]//div"
    xcomponents_selector = "//*[@id='parts-surl-component']/div[position()>1]/div/a"
    ximg_selector = "//*[@id='product-image']"
    xproduct_selector = "//*[@id='component-list']/div/div/div[2]/ul//li/div"
    xproduct_img_selector = "//*[@id='main-product-image']/div[2]/ul/li[1]/a/img"
    xproduct_img_selector2 = "//*[@id='main-product-image']/a/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    # Categorys on yamaha
    for yr in tree.xpath(xpath_selector):
        year = {
            'category_name': 'years',
            'category': yr.text,
            'category_url': yr.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(year)

        # Horse Power scraping
        page = requests.get(
            base_url + year['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xhp_selector):
            if 'ResultHP' in hp.get('class'):
                horse_power = {
                    'category_name': 'horse power',
                    'category': re.sub(r'[\n\t]+', '', hp.xpath('b')[0].text),
                    'category_url': hp.xpath('b')[0].get('href'),
                    'sub_category': []
                }
                year['sub_category'].append(horse_power)
            elif 'result' in hp.get('class') and not hp.xpath('b'):
                if not hp.xpath('a'):
                    print(horse_power)
                    print(base_url + year['category_url'])
                    print(etree.tostring(hp))
                model = {
                    'category_name': 'model',
                    'category': re.sub(r'[\n\t]+', '', hp.xpath('a')[0].text),
                    'category_url': hp.xpath('a')[0].get('href'),
                    'sub_category': []
                }
                horse_power['sub_category'].append(model)
                page = requests.get(
                    base_url + model['category_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcomponents_selector):
                    component = {
                        'category_name': 'component',
                        'category': comp.text,
                        'category_url': comp.get('href'),
                        'products': []
                    }
                    model['sub_category'].append(component)

                    # Products scraping
                    page = requests.get(
                        base_url + component['category_url']
                    )

                    tree = html.fromstring(page.content)
                    image = None
                    a = etree.tostring(tree.xpath('//*[@id="diagram"]')[0])
                    z = re.search(r"xlink:href\", *\"[^\"]*\"", a.decode()).group(0).split(',')

                    if len(z)> 1:
                        image = re.sub(r'[\ \"]', '', z[1])
                        r = requests.get('http:' + image, stream=True)
                        save_downloaded_file('img/boats_net/honda/'+ image.split('/')[-1], r)
                        image = 'img/boats_net/honda/'+ image.split('/')[-1]

                    component['image'] = image
                    count = 0
                    old_diag = -1
                    product = None
                    old_product = None
                    for prod in tree.xpath(xproduct_selector):
                        if 'ma-obs' in prod.get('class'):
                            count = -1
                        elif count == 0:
                            product = {
                                "diagram_number": re.sub(r'[\n\t]', '', prod.text),
                            }

                            if(old_diag == re.sub(r'[\n\t]', '', prod.text)):
                                product["recomended"] = old_product

                            old_product = product
                            old_diag = re.sub(r'[\n\t]', '', prod.text)
                            component['products'].append(product)
                        elif count == 1:
                            product['product'] = prod.xpath('h2/a')[0].text
                            product['product_url'] = prod.xpath('h2/a')[0].get('href')
                            product['part_number'] = prod.xpath('p/a')[0].text
                        elif count == 2:
                            page = requests.get(
                                base_url + product['product_url']
                            )

                            tree = html.fromstring(page.content)

                            # To get images
                            image = None
                            if tree.xpath(xproduct_img_selector):
                                image = tree.xpath(xproduct_img_selector)[0].get('src')
                            elif tree.xpath(xproduct_img_selector2):
                                image = tree.xpath(xproduct_img_selector2)[0].get('src')

                            if image:
                                r = requests.get('http:' + image, stream=True)
                                save_downloaded_file('img/boats_net/honda/'+ image.split('/')[-1], r)
                                image = 'img/boats_net/honda/'+ image.split('/')[-1]

                            product['list_price'] = prod.xpath('div[1]')[0].text

                            # If theres another price
                            if prod.xpath('div[2]'):
                                product['your_price'] = prod.xpath('div[2]')[0].text

                            product['manufacturer'] = "Honda Marine"
                            product['image'] = image
                        elif count == 3:
                            count = -1

                        count += 1
                        counter += 1
                        if counter > 100:
                            catalog['scraping_successful'] = True
                            print('Finishing Boats Net Honda Marine Scraping...\n')
                            with open('boats_net_honda_marine-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return
            else:
                print('Caso especial Honda Marine Boats Net.')


def boatsnet_suzuki_marine_scrapper():
    """Scrapper for Boatnet's Suzuki Parts."""
    # Marineengine base url
    base_url = 'http://www.boats.net'
    # Categorys for scraping
    page = requests.get(
        base_url + '/parts/search/Suzuki/Outboard/parts.html'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "//*[@class='year-link-container']/a"
    xhp_selector = "//*[@id='parts-surl-model']/div[position()>1]//div"
    xcomponents_selector = ("//*[@id='parts-surl-component']/"
                            "div[position()>1]/div/a")
    ximg_selector = "//*[@id='product-image']"
    xproduct_selector = "//*[@id='component-list']/div/div/div[2]/ul//li/div"
    xproduct_img_selector = "//*[@id='main-product-image']/div[2]/ul/li[1]/a/img"
    xproduct_img_selector2 = "//*[@id='main-product-image']/a/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
    # Categorys on yamaha
    for yr in tree.xpath(xpath_selector):
        year = {
            'category_name': 'years',
            'category': yr.text,
            'category_url': yr.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(year)

        # Horse Power scraping
        page = requests.get(
            base_url + year['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xhp_selector):
            if 'ResultHP' in hp.get('class'):
                horse_power = {
                    'category_name': 'horse power',
                    'category': re.sub(r'[\n\t]+', '', hp.xpath('b')[0].text),
                    'category_url': hp.xpath('b')[0].get('href'),
                    'sub_category': []
                }
                year['sub_category'].append(horse_power)
            elif 'result' in hp.get('class') and not hp.xpath('b'):
                if not hp.xpath('a'):
                    print(horse_power)
                    print(base_url + year['category_url'])
                    print(etree.tostring(hp))
                model = {
                    'category_name': 'model',
                    'category': re.sub(r'[\n\t]+', '', hp.xpath('a')[0].text),
                    'category_url': hp.xpath('a')[0].get('href'),
                    'sub_category': []
                }
                horse_power['sub_category'].append(model)
                page = requests.get(
                    base_url + model['category_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcomponents_selector):
                    component = {
                        'category_name': 'component',
                        'category': comp.text,
                        'category_url': comp.get('href'),
                        'products': []
                    }
                    model['sub_category'].append(component)

                    # Products scraping
                    page = requests.get(
                        base_url + component['category_url']
                    )

                    tree = html.fromstring(page.content)
                    image = None
                    a = etree.tostring(tree.xpath('//*[@id="diagram"]')[0])
                    z = re.search(r"xlink:href\", *\"[^\"]*\"", a.decode()).group(0).split(',')

                    if len(z)> 1:
                        image = re.sub(r'[\ \"]', '', z[1])
                        r = requests.get('http:' + image, stream=True)
                        save_downloaded_file('img/boats_net/suzuki/'+ image.split('/')[-1], r)
                        image = 'img/boats_net/suzuki/'+ image.split('/')[-1]

                    component['image'] = image
                    count = 0
                    old_diag = -1
                    product = None
                    old_product = None
                    for prod in tree.xpath(xproduct_selector):
                        if 'ma-obs' in prod.get('class'):
                            count = -1
                        elif count == 0:
                            product = {
                                "diagram_number": re.sub(r'[\n\t]', '', prod.text),
                            }

                            if(old_diag == re.sub(r'[\n\t]', '', prod.text)):
                                product["recomended"] = old_product

                            old_product = product
                            old_diag = re.sub(r'[\n\t]', '', prod.text)
                            component['products'].append(product)
                        elif count == 1:
                            if not prod.xpath('h2/a'):
                                print(base_url + component['category_url'])
                                print(etree.tostring(prod))
                                print(old_diag)
                            product['product'] = prod.xpath('h2/a')[0].text
                            product['product_url'] = prod.xpath('h2/a')[0].get('href')
                            product['part_number'] = prod.xpath('p/a')[0].text
                        elif count == 2:
                            page = requests.get(
                                base_url + product['product_url']
                            )

                            tree = html.fromstring(page.content)

                            # To get images
                            image = None
                            if tree.xpath(xproduct_img_selector):
                                image = tree.xpath(xproduct_img_selector)[0].get('src')
                            elif tree.xpath(xproduct_img_selector2):
                                image = tree.xpath(xproduct_img_selector2)[0].get('src')

                            if image:
                                r = requests.get('http:' + image, stream=True)
                                save_downloaded_file('img/boats_net/suzuki/' + image.split('/')[-1], r)
                                image = 'img/boats_net/suzuki/' + image.split('/')[-1]

                            product['list_price'] = prod.xpath('div[1]')[0].text

                            # If theres another price
                            if prod.xpath('div[2]'):
                                product['your_price'] = prod.xpath('div[2]')[0].text

                            product['manufacturer'] = "Suzuki Marine"
                            product['image'] = image
                        elif count == 3:
                            count = -1

                        count += 1
                        counter += 1
                        if counter > 100:
                            catalog['scraping_successful'] = True
                            print("Finishing Boats Net Suzuki "
                                  "Marine Scraping...\n")
                            with open('boats_net_suzuki_marine-' +
                                      scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return
            else:
                print('Caso especial Suzuki Marine Boats Net.')


def save_downloaded_file(path, r):
    """."""
    if r.status_code == 200:
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
            # Guard against race condition
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)


if __name__ == '__main__':

    ###############################################
    # ------------- Argument Parsing ------------ #
    ###############################################
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
        Usage of the Marine Parts Scrapper Module.
        ------------------------------------------

        '''))
    parser.add_argument('--pretty',
                        help='outputs json in a friendly indented format',
                        action='store_true')

    parser.add_argument(
        '--threaded',
        type=int,
        dest='threads',
        help="Thread processing"
    )

    subparsers = parser.add_subparsers(
        dest='site',
        help="The name of the site to scrap")


    parser_marine_engine = subparsers.add_parser('marine_engine')

    parser_marine_engine.add_argument(
        'manufacturer', type=str,
        choices=["johnson", "mercruiser", "mercury"],
        help="The name of the manufacturer"
    )

    parser_marine_engine.add_argument(
        '--offset', type=int,
        dest='offset',
        help="Initial offset"
    )

    parser_marine_engine.add_argument(
        '--offset2', type=int,
        dest='offset2',
        help="Secondary offset"
    )

    parser_marineeurope = subparsers.add_parser('marineparts_europe')

    parser_marineeurope.add_argument(
        'manufacturer', type=str,
        choices=["volvo"],
        help="The name of the manufacturer"
    )

    parser_marineeurope.add_argument(
        '--offset', type=int,
        dest='offset',
        help="Initial offset"
    )

    parser_marineeurope.add_argument(
        '--offset2', type=int,
        dest='offset2',
        help="Secondary offset"
    )

    parser_boatsnet = subparsers.add_parser('boatsnet')
    parser_boatsnet.add_argument(
        'manufacturer', type=str,
        choices=["yamaha"],
        help="The name of the manufacturer"
    )

    args = parser.parse_args()

    # a site has to be introduced
    if not args.site:
        parser.error(message="Too few arguments")

    # json output mode
    PRETTY_OUTPUT = args.pretty

    # threading processing
    if args.threads:
        THREADS = args.threads
        THREADED = True

    # scrapper offsets
    try:
        if args.offset:
            INIT_OFFSET = args.offset

        if args.offset2:
            INIT_OFFSET_2 = args.offset2
    except AttributeError:
        pass

    ###############################################
    # ----------- Directories creation ---------- #
    ###############################################
    if not os.path.exists(FILE_DIR + '/manuals'):
        os.makedirs(FILE_DIR + '/manuals')

    # get user's input from stdin
    selected_scrapper = "%s %s %s" % (args.site,
                                      args.manufacturer,
                                      THREADED)

    # this dict maps user's input with a scrapper
    OPT_DICT = {
        "marine_engine mercury False": marineengine_mercury_scrapper,
        "marine_engine johnson False": partial(marineengine_johnson_evinrude_scrapper,
                                               INIT_OFFSET),
        "boatsnet yamaha": boatsnet_yamaha_scrapper,
        "marine_engine mercruiser False": marineengine_mercruiser_scrapper,
        "marineparts_europe volvo False": partial(marinepartseurope_volvo_penta_scrapper,
                                                  INIT_OFFSET),
        "marineparts_europe volvo True": partial(threaded_volvo_scrapper, THREADS),
        "marine_engine johnson True": partial(threaded_johnson_evinrude_scrapper, THREADS)
    }

    try:
        selected_scrapper_func = OPT_DICT[selected_scrapper]
    except KeyError as e:
        print("Selected scrapper doesn't exists nor is implemented yet.\n"
              "Current available brands are: mercury, johnson.")
        exit(1)

    ############################################
    # Start the actual Scrapping
    print('Started scraping.')
    print('Ignoring some manuals...')

    selected_scrapper_func()

    print('\nFinished scraping.')
