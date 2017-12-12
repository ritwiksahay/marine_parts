# -*- coding: utf-8 -*-
import requests
import json
import re
import copy

from lxml import html, etree
from datetime import date
from logging.handlers import RotatingFileHandler


''' Not in use
def boatsnet_manufacturers(base_url):
    page = requests.get(
        base_url
    )
    tree = html.fromstring(page.content)
    xpath_selector = """/html/body/div[7]/div[1]/div[2]/div/div/div/div/div/div[2]/div/div[1]//
        *[contains(@class,"manufacturers-thumbs")]/div/div/div/a"""

    return tree.xpath(xpath_selector)


def boats_yamaha_scrapper(base_url, scrap_url):
    page = requests.get(
        scrap_url
    )
    tree = html.fromstring(page.content)
    xpath_selector = "/html/body/div[7]/div/div/div[2]/div[2]/div/div[2]//div/a"
    xpath_years_selector = "/html/body/div[7]/div/div/div[2]/div[2]/div[2]//*[contains(@class, 'year-link-container')]/a"
    # The same selector as the components
    xpath_hp_selector = "/html/body/div[7]/div/div/div[2]/div[2]/div[2]//*[contains(@class, 'column-result')]/a"

    # Get elemnts of manufaturer
    for elem in tree.xpath(xpath_selector):
        src = elem.get('href')
        print(src)
        page = requests.get(
            base_url + src
        )
        years_tree = html.fromstring(page.content)
        # Get element years
        for year in years_tree.xpath(xpath_years_selector):
            year_src = (year.get('href'), year.text)
            print(year_src)
            page = requests.get(
                base_url + year_src[0]
            )
            hp_tree = html.fromstring(page.content)
            # Get different Horse power
            for hp in hp_tree.xpath(xpath_hp_selector):
                hp_src = hp.get('href')
                print(hp_src)
                page = requests.get(
                    base_url + hp_src
                )
                component_tree = html.fromstring(page.content)
                # Get components
                for component in component_tree.xpath(xpath_hp_selector):
                    component_src = (component.get('href'), component.text)
                    print(component_src)


# Scrap categories, years, models and parts from http://www.boats.net/
def boatsnet_scrapper():
    base_url = 'http://www.boats.net'

    manufacturers = boatsnet_manufacturers(base_url)

    # Scrap each manufacturer in a custom way
    for manufacturer in manufacturers:
        img = manufacturer.xpath('img')[0]
        provider = img.get('alt').split()[1]
        img_src = manufacturer.xpath('img')[0].get('src')

        print(provider)
        print(img_src)

        if provider == "Yamaha":
            provider_src = base_url + '/parts/search/' + provider + 'parts.html'
            boats_yamaha_scrapper(base_url, provider_src)
'''


##################################################################
## MARINE ENGINE WEB
##################################################################
def marineengine_mercury_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scraping
    page = requests.get(
        base_url + '/parts/mercury-outboard/index.php'
    )
    tree = html.fromstring(page.content)
    # The selectors goes here so they dont recreate on every cicle
    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/a"
    xcategory_selector = "/html/body/main/div[2]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/div[2]/ul//li/a"
    ximg_selector = "/html/body/main/div[2]/p[1]/img"
    xproduct_selector = "/html/body/main/table//tr"
    xproduct_details_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/table//tr/td/p"
    xproduct_unavailable_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/div/a"
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/p/img"

    scrap_date = str(date.today()).replace(' ', '')
    catalog = {
        'categories': [],
        'scraped_date': scrap_date,
        'scraping_successful': False, 
    }
    # Just for debug purposes
    counter = 1
    
    for cat in tree.xpath(xpath_selector):
        category = {
            'category_name': 'category',
            'category': cat.text,
            'category_url': cat.get('href'),
            'sub_category': []
        }
        catalog['categories'].append(category)

        # Horse Power scraping
        page = requests.get(
            base_url + category['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xcategory_selector):
            horse_power = {
                'category_name': 'horse_power',
                'category': re.sub(r'[\n\t]+', '', hp.text),
                'category_url': hp.get('href'),
                'sub_category': []
            }
            category['sub_category'].append(horse_power)

            # Serial Range scraping
            page = requests.get(
                base_url + horse_power['category_url']
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
                page = requests.get(
                    base_url + serial_range['category_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcomponents_selector):
                    component = {
                        'category_name': 'component',
                        'category': comp.text,
                        'category_url': comp.get('href'),
                        'products': []
                    }
                    serial_range['sub_category'].append(component)

                    # Products scraping
                    page = requests.get(
                        base_url + component['category_url']
                    )
                    #print("component " + component['component_url'])

                    tree = html.fromstring(page.content)
                    image = None

                    if(len(tree.xpath(ximg_selector)) > 0):
                        image = tree.xpath(ximg_selector)[0].get('src')
                    
                    component['image'] = image

                    # products cycle
                    diag_number = -1
                    product = None
                    old_product = None
                    recomended = None
                    for prod in tree.xpath(xproduct_selector):
                        if prod.get('class') is None:
                            product = {
                                'product': re.sub(' +', ' ', prod.xpath('td[3]/a/strong')[0].text),
                                'product_url': prod.xpath('td[3]/a')[0].get('href'),
                                'diagram_number': diag_number
                            }
                            component['products'].append(product)
                            #print(product)

                            # Product details scraping
                            page = requests.get(
                                base_url + product['product_url']
                            )
                            tree = html.fromstring(page.content)
                            prod_image = None

                            if(len(tree.xpath(xproduct_img_selector)) > 0):
                                prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

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
                                        product['part_number'] = value
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
                            diag_number = prod.xpath("td[1]/span/strong")[0].text.replace('#','')

                        if counter > 100:
                            print('Finishing Marine Engine Mercury Scraping...\n')
                            catalog['scraping_successful'] = True
                            with open('marine_engine_mercury-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile, indent=4)
                                pass

                            return


def marineengine_johnson_evinrude_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scraping
    page = requests.get(
        base_url + '/parts/parts.php'
    )
    tree = html.fromstring(page.content)

    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/h3/a"
    xyears_selector = "/html/body/main/div[2]/table/tr[1]/td[1]/ul//li/a"
    #xmanuals_selector = "/html/body/main/div[2]/table/tr/td/div[1]/div[1]/ul//li/a"
    xcomponents_selector = "/html/body/main/div[2]/table/tr/td/div[1]/div[2]/ul//li/a"
    #xmanual_img_selector = "/html/body/main/div/div[1]/img"
    #xmanual_details_selector = "/html/body/main/div/div[2]/table//tr"
    xcomponent_parts_selector = "/html/body/main//div/table//tr"
    xcomponent_img_selector = "/html/body/main/div[2]/div/p[1]/img"
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
    
    # Categorys on johnson_evinrude
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
        for yr in tree.xpath(xyears_selector):
            year = {
                'category_name': 'years',
                'category': yr.text,
                'category_url': yr.get('href'),
                'sub_category': []
            }
            category['sub_category'].append(year)

            page = requests.get(
                base_url + year['category_url']
            )
            tree = html.fromstring(page.content)
            # Horse power cycle
            for hp in tree.xpath(xyears_selector):
                horse_power = {
                    'category_name': 'horse_power',
                    'category': hp.text,
                    'category_url': hp.get('href'),
                    'sub_category': []
                }
                year['sub_category'].append(horse_power)

                page = requests.get(
                    base_url + horse_power['category_url']
                )
                tree = html.fromstring(page.content)
                # Horse power cycle
                for diagrams in tree.xpath(xyears_selector):
                    models = {
                        'category_name': 'model',
                        'category': diagrams.text,
                        'category_url': diagrams.get('href'),
                        'sub_category': []
                    }
                    horse_power['sub_category'].append(models)

                    page = requests.get(
                        base_url + models['category_url']
                    )
                    tree = html.fromstring(page.content)

                    # Parts cycle
                    for comp in tree.xpath(xcomponents_selector):
                        component = {
                            'category_name': 'component',
                            'category': comp.text,
                            'category_url': comp.get('href'),
                            'products': []
                        }
                        models['sub_category'].append(component)

                        page = requests.get(
                            base_url + component['category_url']
                        )
                        tree = html.fromstring(page.content)

                        component_image = None
                        if(len(tree.xpath(xcomponent_img_selector)) > 0):
                            component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

                        component['image'] = component_image

                        diag_number = -1

                        # products cycle
                        product = None
                        old_product = None
                        recomended = None
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
                                print('Finishing Marine Engine johnson_evinrude Scraping...\n')
                                catalog['scraping_successful'] = True
                                with open('marine_engine_johnson_evinrude-' + scrap_date + '.json', 'w') as outfile:
                                    json.dump(catalog, outfile, indent=4)
                                    pass

                                return

                    ''' Ignore manuals (incomplete scraping, just partial)
                    man_image = None

                    if(len(tree.xpath(xmanual_img_selector)) > 0):
                        man_image = tree.xpath(xmanual_img_selector)[0]

                    # Manuals cycle
                    for man in tree.xpath(xmanuals_selector):
                        manual = {'manual': man.text, 'manual_url': man.get('href')}

                        page = requests.get(
                            base_url + manual['manual_url']
                        )
                        second_tree = html.fromstring(page.content)

                        

                        
                        for man_det in second_tree.xpath(xmanual_details_selector):
                            print('MANUAL')
                            count = 0
                            for row in man_det.xpath('td'):
                                if count < 2:
                                    print(etree.tostring(row).decode('utf-8').replace('<span class="strike">', '')
                                        .replace('</span>', '').replace('\t', '').replace('\n', '').split('<br/>')[1])
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
    # Categorys on johnson_evinrude
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
    # Categorys on johnson_evinrude
    for hp in tree.xpath(xpath_selector):
        horse_power = {
            'category_name': 'horse_power',
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
                    print(component)

                    page = requests.get(
                        base_url + component['category_url']
                    )
                    tree = html.fromstring(page.content)

                    component_image = None
                    if(len(tree.xpath(xcomponent_img_selector)) > 0):
                        component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

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

    print(catalog)


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
    # Categorys on johnson_evinrude
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
        tree = html.fromstring(page.content)
        # Years cycle
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
                # Years cycle
                for comp in tree.xpath(xmodel_selector):
                    if not tree.xpath(xpdf_selector):
                        print(comp.get('href'))
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
                        tree = html.fromstring(page.content)
                        # Years cycle
                        for item in tree.xpath(xmodel_selector):
                            if not tree.xpath(xpdf_selector):
                                it = {
                                    'category_name': 'item',
                                    'category': item.xpath('strong')[0].text,
                                    'category_url': item.get('href'),
                                    'sub_category': []
                                }
                                component['sub_category'].append(component)
                                print("ANOTHER LEVEL NEEDED")
                            else:
                                for man in tree.xpath(xpdf_selector):
                                    manual = {
                                        'category_name': 'manual',
                                        'products': man.xpath('strong')[0].text,
                                        'manual_url': man.get('href'),
                                        'image': None,
                                    }
                                    component['sub_category'].append(manual)
                    else:  
                        for man in tree.xpath(xpdf_selector):
                            manual = {
                                'category_name': 'manual',
                                'products': man.xpath('strong')[0].text,
                                'manual_url': man.get('href'),
                                'image': None,
                            }
                            model['sub_category'].append(manual)

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
                    category['sub_category'].append(manual)
                    counter += 1


if __name__ == '__main__':
    print('Started scraping.')
    print('Ignoring some manuals...')

    ##########################################################
    ### MARINE ENGINE ########################################
    ##########################################################
    print('\nMarine Engine web scrapping.')
    print('Starting Marine Engine Mercury Scraping...')
    #marineengine_mercury_scrapper()

    print('\nStarting Marine Engine Mercruiser Scraping...')
    #marineengine_mercruiser_scrapper()
    
    print('\nStarting Marine Engine Johnson & Evinrude Scraping...')
    #marineengine_johnson_evinrude_scrapper()

    print('\nStarting Marine Engine Force scraping...')
    #marineengine_force_scrapper()

    print('\nStarting Marine Engine Mariner scraping...')
    #marineengine_mariner_scrapper()

    print('\nStarting Marine Engine OMC Sterndrive scraping...')
    marineengine_omc_sterndrive_scrapper()

    ###########################################################
    ### MARINE EXPRESS ########################################
    ###########################################################
    print('\nMarine Parts Express web scrapping.')
    print('Starting Marine Express Chrysler Marine Scraping...')
    #marinepartsexpress_chrysler_marine_scrapper()

    print('\nStarting Marine Express Crusader Scraping...')
    #marinepartsexpress_crusader_scrapper()

    print('\nStarting Marine Express Volvo Penta Marine Scraping...')
    #marinepartsexpress_volvo_penta_marine_scrapper()


    print('\nFinished scraping.')
