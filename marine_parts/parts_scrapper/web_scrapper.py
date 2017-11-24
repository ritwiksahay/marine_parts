# -*- coding: utf-8 -*-
import requests
import json
import re

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


def marineengine_mercury_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scrapping
    page = requests.get(
        base_url + '/parts/mercury-outboard/index.php'
    )
    tree = html.fromstring(page.content)
    # The selectors goes here so they dont recreate on every cicle
    xpath_selector = "/html/body/main/div[1]/div[2]/div[1]/div[2]/div/ul//li/a"
    xcategory_selector = "/html/body/main/div[2]/ul//li/a"
    ximg_selector = "/html/body/main/div[2]/p[1]/img"
    xproduct_selector = "/html/body/main/table/tbody//tr"
    xproduct_details_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/table//tr/td/p"
    xproduct_unavailable_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/div/a"
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/p/img"

    catalog = {
        'products': []
    }
    
    for cat in tree.xpath(xpath_selector):
        category = {'category': cat.text, 'category_url': cat.get('href')}

        # Horse Power Scrapping
        page = requests.get(
            base_url + category['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xcategory_selector):
            horse_power = {'horse_power': re.sub(r'[\n\t]', '', hp.text), 'hp_url': hp.get('href')}

            # Serial Range Scrapping
            page = requests.get(
                base_url + horse_power['hp_url']
            )
            tree = html.fromstring(page.content)

            for srange in tree.xpath(xcategory_selector):
                serial_range = {'serial_range': re.sub(r'[\n\t]', '', srange.text), 'serials_url': srange.get('href')}

                # Component Scrapping
                page = requests.get(
                    base_url + serial_range['serials_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcategory_selector):
                    component = {
                        'component': comp.text,
                        'component_url': comp.get('href')
                    }

                    # Products scrapping
                    page = requests.get(
                        base_url + component['component_url']
                    )
                    tree = html.fromstring(page.content)
                    image = None

                    if(len(tree.xpath(ximg_selector)) > 0):
                        image = tree.xpath(ximg_selector)[0]
                    
                    component['image'] = image.get('src')

                    # products cycle
                    counter = 1
                    for prod in tree.xpath(xproduct_selector):
                        count = 0
                        if counter % 2 == 0:
                            product = {
                                'product': prod.xpath('td[3]/a/strong')[0].text,
                                'product_url': prod.xpath('td[3]/a')[0].get('href')
                            }

                            # Product details scrapping
                            page = requests.get(
                                base_url + product['product_url']
                            )
                            tree = html.fromstring(page.content)
                            prod_image = None

                            if(len(tree.xpath(xproduct_img_selector)) > 0):
                                prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

                            product['product_image'] = prod_image

                            recomended = None
                            if tree.xpath(xproduct_unavailable_selector):
                                recomended = tree.xpath(xproduct_unavailable_selector)[0].get('href').replace(' ', '20%')

                            # Assemble the porduct json object
                            product['recomended'] = recomended
                            product['category'] = category
                            product['horse_power'] = horse_power
                            product['serial_range'] = serial_range
                            product['component'] = component 

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

                            catalog['products'].append(product)

                            if counter > 20:
                                with open('marineengine_mercury.json', 'w') as outfile:
                                    json.dump(catalog, outfile)

                                print(catalog)
                                return

                        counter += 1


def marineengine_evinrude_scrapper():
    # Marineengine base url
    base_url = 'https://www.marineengine.com'
    # Categorys scrapping
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
    xcomponent_parts_selector = "/html/body/main/div[2]/table/tr[2]//td//a"
    xcomponent_img_selector = "/html/body/main/div[2]/div/p[1]/img"
    xproduct_details_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/table//tr/td/p"
    xproduct_unavailable_selector = "/html/body/main/div[1]/div[1]/div[1]/div[2]/div/a"
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/p/img"

    catalog = {
        'products': []
    }
    
    # Categorys on evinrude
    for cat in tree.xpath(xpath_selector):
        category = {'category': cat.text, 'category_url': cat.get('href')}

        page = requests.get(
            base_url + category['category_url']
        )
        tree = html.fromstring(page.content)
        # Years cycle
        for yr in tree.xpath(xyears_selector):
            year = {'year': yr.text, 'year_url': yr.get('href')}

            page = requests.get(
                base_url + year['year_url']
            )
            tree = html.fromstring(page.content)
            # Horse power cycle
            for hp in tree.xpath(xyears_selector):
                horse_power = {'horse_power': hp.text, 'hp_url': hp.get('href')}

                page = requests.get(
                    base_url + horse_power['hp_url']
                )
                tree = html.fromstring(page.content)
                # Horse power cycle
                for diagrams in tree.xpath(xyears_selector):
                    models = {'model': diagrams.text, 'model_url': diagrams.get('href')}

                    page = requests.get(
                        base_url + models['model_url']
                    )
                    tree = html.fromstring(page.content)

                    # Parts cycle
                    for comp in tree.xpath(xcomponents_selector):
                        component = {'component': comp.text, 'component_url': comp.get('href')}

                        page = requests.get(
                            base_url + component['component_url']
                        )
                        tree = html.fromstring(page.content)

                        if(len(tree.xpath(xcomponent_img_selector)) > 0):
                            component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

                        component['image'] = component_image

                        counter = 0
                        # products cycle
                        for part_det in tree.xpath(xcomponent_parts_selector):
                            if 'cart' not in part_det.get('href'):
                                page = requests.get(
                                    base_url + part_det.get('href')
                                )
                                tree = html.fromstring(page.content)
                                product = {'product_url': part_det.get('href')}
                                prod_image = None

                                if(len(tree.xpath(xproduct_img_selector)) > 0):
                                    prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

                                product['product_image'] = prod_image

                                recomended = None
                                if tree.xpath(xproduct_unavailable_selector):
                                    recomended = tree.xpath(xproduct_unavailable_selector)[0].get('href').replace(' ', '20%')

                                # Assemble the porduct json object
                                product['recomended'] = recomended
                                product['category'] = category
                                product['horse_power'] = horse_power
                                product['component'] = component

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

                                catalog['products'].append(product)
                                counter += 1
                                print(counter)
                                if counter > 5:

                                    with open('marineengine_envinrude.json', 'w') as outfile:
                                        json.dump(catalog, outfile)

                                    #print(catalog)
                                    print('Ignoring manuals')
                                    return

                    print('Ignoring manuals')
                    ''' Ignore manuals (incomplete scrapping, just partial)
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


if __name__ == '__main__':
    print('Started Scrapping.')
    print('Starting Marine Engine Mercury Scrarpping...')
    marineengine_mercury_scrapper()
    print('Starting Marine Engine Evinrude Scrarpping...')
    marineengine_evinrude_scrapper()
    print('Finished Scrapping.')
