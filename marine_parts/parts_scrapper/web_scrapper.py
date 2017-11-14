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


if __name__ == '__main__':
    boatsnet_scrapper()
