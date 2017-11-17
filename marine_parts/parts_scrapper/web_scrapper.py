# -*- coding: utf-8 -*-
import requests
import json
import re

from lxml import html, etree
from datetime import date
from logging.handlers import RotatingFileHandler


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
    xproduct_img_selector = "/html/body/main/div[1]/div[1]/div[1]/div[1]/p/img"
    
    for cat in tree.xpath(xpath_selector):
        category = (cat.text, cat.get('href'))
        print(category)

        # Horse Power Scrapping
        page = requests.get(
            base_url + category[1]
        )
        tree = html.fromstring(page.content)

        for hp in tree.xpath(xcategory_selector):
            horse_power = (re.sub(r'[\n\t]', '', hp.text), hp.get('href'))
            print(horse_power)

            # Serial Range Scrapping
            page = requests.get(
                base_url + horse_power[1]
            )
            tree = html.fromstring(page.content)

            for srange in tree.xpath(xcategory_selector):
                serial_range = (re.sub(r'[\n\t]', '', srange.text), srange.get('href'))
                print(serial_range)

                # Component Scrapping
                page = requests.get(
                    base_url + serial_range[1]
                )
                tree = html.fromstring(page.content)

                for comp in tree.xpath(xcategory_selector):
                    component = (comp.text, comp.get('href'))
                    print(component)

                    # Products scrapping
                    page = requests.get(
                        base_url + component[1]
                    )
                    tree = html.fromstring(page.content)
                    image = None

                    if(len(tree.xpath(ximg_selector)) > 0):
                        image = tree.xpath(ximg_selector)[0]
                    
                    counter = 1
                    for prod in tree.xpath(xproduct_selector):
                        count = 0
                        if counter % 2 == 0:
                            product = (prod.xpath('td[3]/a/strong')[0].text, prod.xpath('td[3]/a')[0].get('href'))
                            print(product)

                            # Product details scrapping
                            page = requests.get(
                                base_url + product[1]
                            )
                            tree = html.fromstring(page.content)
                            prod_image = None

                            if(len(tree.xpath(xproduct_img_selector)) > 0):
                                prod_image = tree.xpath(xproduct_img_selector)[0]

                            print(etree.tostring(prod_image))

                            for details in tree.xpath(xproduct_details_selector):
                                value = (etree.tostring(details).decode('utf-8').replace('\n', '').replace('\t', '').replace('</p>', '')
                                    .replace('<strong>', '').replace('</strong>', '').replace('<p>', '').split('<br/>')[1]
                                    .replace('&#8212;', '').replace('&#160;', ' '))
                                if count == 0:
                                    print(value)
                                elif count == 1:
                                    print(value)
                                elif count == 2:
                                    print(value)
                                else:
                                    print(value)

                                count += 1

                            if counter > 4:
                                return

                        counter += 1


if __name__ == '__main__':
    marineengine_mercury_scrapper()
