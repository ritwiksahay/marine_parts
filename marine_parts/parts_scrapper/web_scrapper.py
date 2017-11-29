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
            'category': cat.text,
            'category_url': cat.get('href'),
            'horse_power': []
        }
        catalog['categories'].append(category)

        # Horse Power scraping
        page = requests.get(
            base_url + category['category_url']
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xcategory_selector):
            horse_power = {
                'horse_power': re.sub(r'[\n\t]', '', hp.text),
                'hp_url': hp.get('href'),
                'serial_range': []
            }
            category['horse_power'].append(horse_power)

            # Serial Range scraping
            page = requests.get(
                base_url + horse_power['hp_url']
            )
            tree = html.fromstring(page.content)

            for srange in tree.xpath(xcategory_selector):
                serial_range = {
                    'serial_range': re.sub(r'[\n\t]', '', srange.text),
                    'serials_url': srange.get('href'),
                    'components': []
                }
                horse_power['serial_range'].append(serial_range)

                # Component scraping
                page = requests.get(
                    base_url + serial_range['serials_url']
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcomponents_selector):
                    component = {
                        'component': comp.text,
                        'component_url': comp.get('href'),
                        'products': []
                    }
                    serial_range['components'].append(component)

                    # Products scraping
                    page = requests.get(
                        base_url + component['component_url']
                    )
                    #print("component " + component['component_url'])

                    tree = html.fromstring(page.content)
                    image = None

                    if(len(tree.xpath(ximg_selector)) > 0):
                        image = tree.xpath(ximg_selector)[0].get('src')
                    
                    component['image'] = image

                    # products cycle
                    diag_number = -1
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

                            recomended = None
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

                            counter += 1
                        else:
                            diag_number = prod.xpath("td[1]/span/strong")[0].text

                        if counter > 10:
                            catalog['scraping_successful'] = True
                            with open('marineengine_mercury-' + scrap_date + '.json', 'w') as outfile:
                                json.dump(catalog, outfile)
                                pass

                            print(catalog)
                            return


def marineengine_evinrude_scrapper():
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
    
    # Categorys on evinrude
    for cat in tree.xpath(xpath_selector):
        category = {
            'category': cat.text,
            'category_url': cat.get('href'),
            'years': []
        }
        catalog['categories'].append(category)

        page = requests.get(
            base_url + category['category_url']
        )
        print("aca " + category['category_url'])
        tree = html.fromstring(page.content)
        # Years cycle
        for yr in tree.xpath(xyears_selector):
            year = {
                'year': yr.text,
                'year_url': yr.get('href'),
                'horse_power': []
            }
            category['years'].append(year)

            page = requests.get(
                base_url + year['year_url']
            )
            print("aca2 " + year['year_url'])
            tree = html.fromstring(page.content)
            # Horse power cycle
            for hp in tree.xpath(xyears_selector):
                horse_power = {
                    'horse_power': hp.text,
                    'hp_url': hp.get('href'),
                    'models': []
                }
                year['horse_power'].append(horse_power)

                page = requests.get(
                    base_url + horse_power['hp_url']
                )
                print("aca3 " + horse_power['hp_url'])
                tree = html.fromstring(page.content)
                # Horse power cycle
                for diagrams in tree.xpath(xyears_selector):
                    models = {
                        'model': diagrams.text,
                        'model_url': diagrams.get('href'),
                        'components': []
                    }
                    horse_power['models'].append(models)

                    page = requests.get(
                        base_url + models['model_url']
                    )
                    print("aca4 " + models['model_url'])
                    tree = html.fromstring(page.content)

                    # Parts cycle
                    for comp in tree.xpath(xcomponents_selector):
                        component = {
                            'component': comp.text,
                            'component_url': comp.get('href'),
                            'products': []
                        }
                        models['components'].append(component)

                        page = requests.get(
                            base_url + component['component_url']
                        )
                        print(component['component_url'])
                        tree = html.fromstring(page.content)

                        if(len(tree.xpath(xcomponent_img_selector)) > 0):
                            component_image = tree.xpath(xcomponent_img_selector)[0].get('src')

                        component['image'] = component_image

                        diag_number = -1

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
                                    print(product['product_url'] + str(product))
                                    tree = html.fromstring(page.content)
                                    prod_image = None

                                    if(len(tree.xpath(xproduct_img_selector)) > 0):
                                        prod_image = tree.xpath(xproduct_img_selector)[0].get('src')

                                    product['product_image'] = prod_image

                                    recomended = None
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
                                    counter += 1
                            else:
                                if prod.xpath('td/span/strong'):
                                    diag_number = prod.xpath("td/span/strong")[0].text

                            if counter > 10:
                                catalog['scraping_successful'] = True
                                with open('marineengine_envinrude-' + scrap_date + '.json', 'w') as outfile:
                                    json.dump(catalog, outfile)
                                    pass

                                print(catalog)
                                print('Ignoring manuals')
                                return

                    print('Ignoring manuals')
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


if __name__ == '__main__':
    print('Started scraping.')
    print('Starting Marine Engine Mercury Scraping...')
    marineengine_mercury_scrapper()
    print('\nStarting Marine Engine Evinrude Scraping...')
    marineengine_evinrude_scrapper()
    print('Finished scraping.')
