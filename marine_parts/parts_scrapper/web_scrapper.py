# -*- coding: utf-8 -*-

import copy
import json
import requests
import os
import re
import sys

from urllib import parse
from lxml import html, etree
from datetime import date
# from logging.handlers import RotatingFileHandler

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
MARINE_ENGINE_BASE_URL = 'https://www.marineengine.com'


def create_output_file(data, path):
    """Dump the json data into a file."""
    data['scraping_successful'] = True
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    data['sub_category'] = []


def request_get(path, stream=False):
    """Execute a GET request and returns contents."""
    try:
        return requests.get(path, stream=stream)
    except Exception as e:
        print(e)


##################################################################
# MARINE ENGINE WEB ##############################################
##################################################################


def marineengine_mercury_scrapper():
    """Scrapper for Marine Engine Mercury Parts."""
    # Marineengine base url
    global MARINE_ENGINE_BASE_URL, FILE_DIR

    print('Starting Marine Engine Mercury Scraping...')
    # Categorys scraping
    page = request_get(
        MARINE_ENGINE_BASE_URL + '/parts/mercury-outboard/index.php'
    )
    tree = html.fromstring(page.content)
    # The selectors goes here so they dont recreate on every cicle
    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/a"
    xcategory_selector = "/html/body/main/div[2]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/div[2]/ul//li/a"
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

    for cat in tree.xpath(xpath_selector)[0:1]:
        if not os.path.exists(FILE_DIR + '/marine_engine/mercury/' + cat.text):
            os.makedirs(FILE_DIR + '/marine_engine/mercury/' + cat.text)
        category = {
            'category_name': 'category',
            'category': cat.text,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        # Horse Power scraping
        page = request_get(
            MARINE_ENGINE_BASE_URL + category['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xcategory_selector)[0:5]:
            cat_name = re.sub(r'[\n\t]+', '', hp.text)
            print("'%s' starting...\n" % cat_name)
            horse_power = {
                'category_name': 'horse power',
                'category': cat_name,
                'category_url': hp.get('href'),
                'sub_category': []
            }
            category['sub_category'].append(horse_power)

            # Serial Range scraping
            page = request_get(
                MARINE_ENGINE_BASE_URL + horse_power['category_url']
            )
            tree = html.fromstring(page.content)

            for srange in tree.xpath(xcategory_selector):
                serial_range = {
                    'category_name': 'serial_range',
                    'category': re.sub(r'[\n\t]+', '', srange.text),
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
                    component = {
                        'category_name': 'component',
                        'category': comp.text,
                        'category_url': comp.get('href'),
                        'products': []
                    }

                    print("Scrapping component '%s' \n\turl: %s"
                          % (component['category'], component['category_url']))

                    serial_range['sub_category'].append(component)

                    # Products scraping
                    page = request_get(
                        MARINE_ENGINE_BASE_URL + component['category_url']
                    )

                    tree = html.fromstring(page.content)

                    component_image = None

                    if(len(tree.xpath(ximg_selector)) > 0):
                        component_image = tree.xpath(ximg_selector)[0] \
                            .get('src')

                    if component_image:
                        r = request_get(component_image, stream=True)
                        save_downloaded_file(
                            FILE_DIR +
                            '/img/marine_engine/mercury/' +
                            component_image.split('/')[-1], r)
                        component_image = 'img/marine_engine/mercury/' + \
                            component_image.split('/')[-1]

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

                            product = {
                                'product': re.sub(' +', ' ', title),
                                'diagram_number': diag_number,
                                'replacements': []
                            }

                            # Check if it's unavailable obsolete and replaced
                            is_replaced = False
                            if prod.xpath('td[3]/small[1]'):
                                product['is_available'] = False
                                xpath = prod.xpath('td[3]/small[2]/br')
                                if xpath is not None and xpath != []:
                                    match = xpath[0].tail.strip()
                                    is_replaced = "Replaced" in match
                            else:
                                product['is_available'] = True

                            # Product details scraping
                            page = request_get(
                                MARINE_ENGINE_BASE_URL + url
                            )
                            tree = html.fromstring(page.content)

                            count = 0
                            # Price and other details from the product page
                            for details in tree.xpath(
                                    xproduct_details_selector)[2:]:
                                value = \
                                    etree.tostring(details) \
                                    .decode('utf-8') \
                                    .replace('\n', '') \
                                    .replace('\t', '') \
                                    .replace('</p>', '') \
                                    .replace('<strong>', '') \
                                    .replace('</strong>', '') \
                                    .replace('<p>', '').split('<br/>')[1] \
                                    .replace('&#8212;', '') \
                                    .replace('&#160;', ' ')

                                if value:
                                    if count == 0:
                                        product['part_number'] = value
                                    else:
                                        product['manufacturer'] = value

                                count += 1

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

            print("\n'%s' done...\n" % cat_name)
            output_file_path = FILE_DIR + '/marine_engine/mercury/' + \
                cat.text + '/' + re.sub(r'/', r'\\', cat_name.strip()) + \
                '.json'
            create_output_file(catalog, output_file_path)


def marineengine_johnson_evinrude_scrapper():
    """Scrapper for Marine Engine Johnson Evinrude Parts."""
    # Marineengine base url
    global MARINE_ENGINE_BASE_URL

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
        if not os.path.exists(FILE_DIR + '/marine_engine/j&e/' + cat.text):
            os.makedirs(FILE_DIR + '/marine_engine/j&e/' + cat.text)
        category = {
            'category_name': 'category',
            'category': cat.text,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        page = request_get(
            MARINE_ENGINE_BASE_URL + category['category_url']
        )
        tree = html.fromstring(page.content)
        # Years cycle
        for yr in tree.xpath(xyears_selector)[0:1]:
            if not os.path.exists(FILE_DIR + '/marine_engine/j&e/' +
                                  re.sub(r'/', r'\\', cat.text) + '/' +
                                  yr.text):
                os.makedirs(FILE_DIR + '/marine_engine/j&e/' +
                            re.sub(r'/', r'\\', cat.text) +
                            '/' + yr.text)
            year = {
                'category_name': 'years',
                'category': yr.text,
                'category_url': yr.get('href'),
                'sub_category': []
            }
            category['sub_category'].append(year)

            page = request_get(
                MARINE_ENGINE_BASE_URL + year['category_url']
            )
            tree = html.fromstring(page.content)
            # Horse power cycle
            for hp in tree.xpath(xyears_selector)[0:1]:
                cat_name = re.sub(r'[\n\t]+', '', hp.text)
                horse_power = {
                    'category_name': 'horse power',
                    'category': cat_name,
                    'category_url': hp.get('href'),
                    'sub_category': []
                }
                year['sub_category'].append(horse_power)

                page = request_get(
                    MARINE_ENGINE_BASE_URL + horse_power['category_url']
                )
                tree = html.fromstring(page.content)
                # Horse power cycle
                for diagrams in tree.xpath(xyears_selector)[0:1]:
                    models = {
                        'category_name': 'model',
                        'category': diagrams.text,
                        'category_url': diagrams.get('href'),
                        'sub_category': []
                    }
                    horse_power['sub_category'].append(models)

                    page = request_get(
                        MARINE_ENGINE_BASE_URL + models['category_url']
                    )
                    tree = html.fromstring(page.content)

                    # Parts cycle
                    for comp in tree.xpath(xcomponents_selector)[0:1]:
                        component = {
                            'category_name': 'component',
                            'category': comp.text,
                            'category_url': comp.get('href'),
                            'products': []
                        }

                        print("Scrapping component '%s' \n\turl: %s"
                              % (component['category'],
                                 component['category_url']))

                        models['sub_category'].append(component)

                        page = request_get(
                            MARINE_ENGINE_BASE_URL + component['category_url']
                        )
                        tree = html.fromstring(page.content)

                        component_image = None
                        if(len(tree.xpath(xcomponent_img_selector)) > 0):
                            component_image = \
                                tree.xpath(xcomponent_img_selector)[0] \
                                .get('src')

                        if component_image:
                            r = request_get(MARINE_ENGINE_BASE_URL +
                                            component_image,
                                            stream=True)
                            save_downloaded_file(
                                FILE_DIR +
                                '/img/marine_engine/j&e/' +
                                component_image.split('/')[-1], r)
                            component_image = 'img/marine_engine/j&e/' + \
                                component_image.split('/')[-1]

                        component['image'] = component_image

                        # products cycle
                        diag_number = -1
                        product = None
                        last_replaced = None
                        for prod in tree.xpath(xcomponent_parts_selector):
                            if prod.get('class') is None:
                                name = ''
                                link = ''

                                if prod.xpath('td[3]/a/strong'):
                                    name = \
                                        re.sub(' +',
                                               ' ',
                                               prod.xpath('td[3]/a/strong')[0]
                                               .text)
                                    link = prod.xpath('td[3]/a')[0].get('href')
                                elif prod.xpath('td[3]/p/strong/a'):
                                    name = \
                                        re.sub(
                                            ' +',
                                            ' ',
                                            prod.xpath('td[3]/p/strong/a')[0]
                                            .text)
                                    link = prod.xpath('td[3]/p/strong/a')[0] \
                                        .get('href')

                                if name and link:
                                    product = {
                                        'product': name,
                                        'diagram_number': diag_number,
                                        'replacements': []
                                    }

                                    # Check if it's unavailable obsolete and
                                    # replaced
                                    is_replaced = False
                                    if prod.xpath('td[3]/small[1]'):
                                        product['is_available'] = False
                                        xpath = prod.xpath('td[3]/small[2]/br')
                                        if xpath is not None and xpath != []:
                                            match = xpath[0].tail.strip()
                                            is_replaced = "Replaced" in match
                                    else:
                                        product['is_available'] = True

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
                                                product['part_number'] = \
                                                    value.split()[0]
                                            else:
                                                product['manufacturer'] = value

                                        count += 1

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
                                            .text.replace('#', '')

                print("\n'%s' done...\n" % yr.text)
                output_file_path = FILE_DIR + '/marine_engine/j&e/' + \
                    re.sub(r'/', r'\\', cat.text) + "/" + \
                    yr.text + "/" + re.sub(r'/', r'\\', cat_name) + \
                    '.json'
                create_output_file(catalog, output_file_path)

                ''' Ignore manuals (incomplete scraping, just partial)
                man_image = None

                if(len(tree.xpath(xmanual_img_selector)) > 0):
                    man_image = tree.xpath(xmanual_img_selector)[0]

                # Manuals cycle
                for man in tree.xpath(xmanuals_selector):
                    manual = \
                        {'manual': man.text, 'manual_url': man.get('href')}

                    page = requests.get(
                        MARINE_ENGINE_BASE_URL + manual['manual_url']
                    )
                    second_tree = html.fromstring(page.content)

                    for man_det in second_tree.xpath(xmanual_details_selector):
                        print('MANUAL')
                        count = 0
                        for row in man_det.xpath('td'):
                            if count < 2:
                                print(etree.tostring(row).decode('utf-8')
                                    .replace('<span class="strike">', '')
                                    .replace('</span>', '').replace('\t', '')
                                    .replace('\n', '').split('<br/>')[1])
                            count += 1

                        print('HEREEE')
                        count = 0
                        for row in man_det.xpath('td/p'):
                            if count == 1:
                                print(etree.tostring(row))
                            else:
                                print(etree.tostring(row))
                            count += 1
                '''


def marineengine_mercruiser_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scraping
    page = requests.get(
        base_url + '/parts/mercruiser-stern-drive/index.php'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/a"
    xmodel_selector = "/html/body/main/div[2]/ul//li/a"
    xserial_range_selector = "/html/body/main/div[2]/ul//li/a"
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
    # Categorys on mercruiser scrapper
    for cat in tree.xpath(xpath_selector):
        category = {
            'category_name': 'category',
            'category': cat.text,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        page = requests.get(
            base_url + category['category_url']
        )
        tree = html.fromstring(page.content)
        # Years cycle
        for mod in tree.xpath(xmodel_selector):
            model = {
                'category_name': 'model',
                'category': mod.text,
                'category_url': mod.get('href'),
                'sub_category': []
            }
            category['sub_category'].append(model)

            page = requests.get(
                base_url + model['category_url']
            )
            tree = html.fromstring(page.content)
            for sr in tree.xpath(xserial_range_selector):
                serial_range = {
                    'category_name': 'serial_range',
                    'category': re.sub(r'[\n\t]+', '', sr.text),
                    'category_url': sr.get('href'),
                    'sub_category': []
                }
                model['sub_category'].append(serial_range)
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
                    print("Caso especial mercruiser")

                for comp in comps:
                    component = {
                        'category_name': 'component',
                        'category': comp.text,
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
                        save_downloaded_file('img/marine_engine/mercruiser/'+ component_image.split('/')[-1], r)
                        component_image = 'img/marine_engine/mercruiser/'+ component_image.split('/')[-1]

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
                                    save_downloaded_file('img/marine_engine/mercruiser/'+ prod_image.split('/')[-1], r)
                                    prod_image = 'img/marine_engine/mercruiser/'+ prod_image.split('/')[-1]
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

                        if counter > 100:
                            print('Finishing Marine Engine Mercruiser Scraping...\n')
                            catalog['scraping_successful'] = True
                            with open('marine_engine_mercruiser-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return


def marineengine_force_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scraping
    page = requests.get(
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

    xpath_selector = "/html/body/div/div[2]/div[1]/section[1]/blockquote/ul//li/a"
    xpath_selector2 = "/html/body/div/div[2]/div[1]/section[1]/table//tr/td"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False,
    }

    counter = 0
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
            r = requests.get(man_url + manual['manual_url'].replace(' ', '%20'), stream=True)
            save_downloaded_file('manuals/marine_express/crusader/'+ manual['manual_url'].split('/')[-1], r)
            manual['manual_url'] = 'manuals/marine_express/crusader/'+ manual['manual_url'].split('/')[-1]

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
                r = requests.get(man_url + manual['manual_url'].replace(' ', '%20'), stream=True)
                save_downloaded_file('manuals/marine_express/crusader/'+ manual['manual_url'].split('/')[-1], r)
                manual['manual_url'] = 'manuals/marine_express/crusader/'+ manual['manual_url'].split('/')[-1]

    catalog['scraping_successful'] = True
    print('Finishing Marine Parts Express Crusader Manuals Scraping...\n')
    with open('marine_parts_express_crusader-' + scrap_date + '.json', 'w') as outfile:
        json.dump(catalog, outfile, indent=4)
        pass


def marinepartsexpress_volvo_penta_marine_scrapper():
    base_url = 'http://www.marinepartsexpress.com'
    # Categorys scraping
    page = requests.get(
        base_url + '/VP_Schematics/directory.php'
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
    # Categorys on johnson_evinrude
    for item in tree.xpath(xpath_selector):
        category = {
            'category_name': 'category',
            'category': item.xpath('strong')[0].text,
            'category_url': item.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        page = requests.get(
            base_url + category['category_url']
        )

        print(base_url + category['category_url'] + " ACAA1")
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

                page = requests.get(
                    base_url + model['category_url']
                )
                tree = html.fromstring(page.content)
                print(base_url + model['category_url'] + " ACAA2")
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

                        page = requests.get(
                            base_url + component['category_url']
                        )
                        print(base_url + component['category_url'] + " ACA3")
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
                                    url = manual['manual_url'].replace("viewer.php?pdf=", "").split("&breadcrumb")[0]
                                    url = parse.unquote(url).replace('+', '%20')
                                    r = requests.get(url, stream=True)
                                    save_downloaded_file('manuals/marine_express/volvo/'+ url.split('/')[-1], r)
                                    manual['manual_url'] = 'manuals/marine_express/volvo/'+ url.split('/')[-1]
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
                                url = manual['manual_url'].replace("viewer.php?pdf=", "").split("&breadcrumb")[0]
                                url = parse.unquote(url).replace('+', '%20')
                                print(url)
                                r = requests.get(url, stream=True)
                                save_downloaded_file('manuals/marine_express/volvo/'+ url.split('/')[-1], r)
                                manual['manual_url'] = 'manuals/marine_express/volvo/'+ url.split('/')[-1]

                            counter += 1

                    if counter > 15:
                        catalog['scraping_successful'] = True
                        print('Finishing Marine Parts Express Volvo Penta Marine Manuals Scraping...\n')
                        with open('marine_parts_express_volvo_penta_marine-' + scrap_date + '.json', 'w') as outfile:
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
                            url = manual['manual_url'].replace("viewer.php?pdf=", "").split("&breadcrumb")[0]
                            url = parse.unquote(url).replace('+', '%20')
                            print(url + " here")
                            r = requests.get(url, stream=True)
                            save_downloaded_file('manuals/marine_express/volvo/'+ url.split('/')[-1], r)
                            manual['manual_url'] = 'manuals/marine_express/volvo/'+ url.split('/')[-1]

                    model = {
                        'category_name': 'model',
                        'category': mod.xpath('strong')[0].text,
                        'category_url': mod.get('href'),
                        'sub_category': []
                    }
                    category['sub_category'].append(model)

                    page = requests.get(
                        base_url + model['category_url']
                    )
                    tree = html.fromstring(page.content)
                    print(base_url + model['category_url'] + " ACAA2")
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

                            page = requests.get(
                                base_url + component['category_url']
                            )
                            print(base_url + component['category_url'] + " ACA3")
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
                                        url = manual['manual_url'].replace("viewer.php?pdf=", "").split("&breadcrumb")[0]
                                        url = parse.unquote(url).replace('+', '%20')
                                        r = requests.get(url, stream=True)
                                        save_downloaded_file('manuals/marine_express/volvo/'+ url.split('/')[-1], r)
                                        manual['manual_url'] = 'manuals/marine_express/volvo/'+ url.split('/')[-1]

                    counter += 1


##################################################################
## BOATS NET
'''
Yamaha 
http://www.boats.net/parts/search/Yamaha/Outboard/parts.html

Honda Marine
http://www.boats.net/parts/search/Honda/Outboard%20Engine/parts.html

Suzuki Marine
http://www.boats.net/parts/search/Suzuki/Outboard/parts.html
'''
##################################################################
def boatsnet_yamaha_scrapper():
    # boatsnet base url
    base_url = 'http://www.boats.net'
    # Categorys scraping
    page = requests.get(
        base_url + '/parts/search/Yamaha/Outboard/parts.html'
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
    # Categorys to scrap on boatsnet yamaha
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
                        save_downloaded_file('img/boats_net/yamaha/'+ image.split('/')[-1], r)
                        image = 'img/boats_net/yamaha/'+ image.split('/')[-1]
                    
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
                                save_downloaded_file('img/boats_net/yamaha/'+ image.split('/')[-1], r)
                                image = 'img/boats_net/yamaha/'+ image.split('/')[-1]

                            product['list_price'] = prod.xpath('div[1]')[0].text

                            # If theres another price
                            if prod.xpath('div[2]'):
                                product['your_price'] = prod.xpath('div[2]')[0].text

                            product['manufacturer'] = "Yamaha"
                            product['image'] = image
                        elif count == 3:
                            count = -1

                        count += 1
                        counter += 1
                        if counter > 100:
                            catalog['scraping_successful'] = True
                            print('Finishing Boats Net Yamaha Scraping...\n')
                            with open('boats_net_yamaha-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return
            else:
                print('Caso especial Yamaha Boats Net.')


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
    # Marineengine base url
    base_url = 'http://www.boats.net'
    # Categorys for scraping
    page = requests.get(
        base_url + '/parts/search/Suzuki/Outboard/parts.html'
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
                            print('Finishing Boats Net Suzuki Marine Scraping...\n')
                            with open('boats_net_suzuki_marine-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass
                            return
            else:
                print('Caso especial Suzuki Marine Boats Net.')


def save_downloaded_file(path, r):
    """."""
    if r.status_code == 200:
        with open(path, 'wb') as f:
            for chunk in r:
                f.write(chunk)


if __name__ == '__main__':

    # Check stdin params
    if len(sys.argv) != 3:
        print("Invalid format.\nMust be: "
              "python3 part_scrapper.py [page] [brand].\n"
              "For example: python3 part_scrapper.py marine_engine johnson\n"
              "Current available brands are: mercury, johnson.")

        exit(1)

    # Create needed directories
    if not os.path.exists(FILE_DIR + '/img'):
        os.makedirs(FILE_DIR + '/img')
    if not os.path.exists(FILE_DIR + '/manuals'):
        os.makedirs(FILE_DIR + '/manuals')

    ###############################################
    # Marine Engine Directories and sub-directories
    # Subdirs

    if not os.path.exists(FILE_DIR + '/img/marine_engine/mercury'):
        os.makedirs(FILE_DIR + '/img/marine_engine/mercury')

    if not os.path.exists(FILE_DIR + '/img/marine_engine/j&e'):
        os.makedirs(FILE_DIR + '/img/marine_engine/j&e')

    """ Is this necessary?
    if not os.path.exists('img/marine_engine/mercruiser'):
        os.makedirs('img/marine_engine/mercruiser')
    
    if not os.path.exists('img/marine_engine/force'):
        os.makedirs('img/marine_engine/force')
    if not os.path.exists('img/marine_engine/mariner'):
        os.makedirs('img/marine_engine/mariner')
    if not os.path.exists('img/marine_engine/omc'):
        os.makedirs('img/marine_engine/omc')

    ################################################
    # Marine Express Directories and sub-directories
    if not os.path.exists('img/marine_express'):
        os.makedirs('img/marine_express')
    if not os.path.exists('manuals/marine_express'):
        os.makedirs('manuals/marine_express')

    # Subdirs
    if not os.path.exists('img/marine_express/chrysler'):
        os.makedirs('img/marine_express/chrysler')
    if not os.path.exists('img/marine_express/crusader'):
        os.makedirs('img/marine_express/crusader')
    if not os.path.exists('manuals/marine_express/crusader'):
        os.makedirs('manuals/marine_express/crusader')
    if not os.path.exists('img/marine_express/volvo'):
        os.makedirs('img/marine_express/volvo')
    if not os.path.exists('manuals/marine_express/volvo'):
        os.makedirs('manuals/marine_express/volvo')

    ############################################
    # Boats Net Directories and sub-directories
    if not os.path.exists('img/boats_net'):
        os.makedirs('img/boats_net')

    # Subdirs
    if not os.path.exists('img/boats_net/yamaha'):
        os.makedirs('img/boats_net/yamaha')
    if not os.path.exists('img/boats_net/honda'):
        os.makedirs('img/boats_net/honda')
    if not os.path.exists('img/boats_net/suzuki'):
        os.makedirs('img/boats_net/suzuki')

    """

    # get user's input from stdin
    selected_scrapper = "%s %s" % (sys.argv[1],
                                   sys.argv[2])

    # this dict maps user's input with a scrapper
    OPT_DICT = {
        "marine_engine mercury": marineengine_mercury_scrapper,
        "marine_engine johnson": marineengine_johnson_evinrude_scrapper,
    }

    ############################################
    # Start the actual Scrapping
    print('Started scraping.')
    print('Ignoring some manuals...')

    try:
        OPT_DICT[selected_scrapper]()
    except KeyError:
        print("Selected scrapper doesn't exists nor is implemented yet.\n"
              "Current available brands are: mercury, johnson.")
        exit(1)

    print('\nFinished scraping.')
