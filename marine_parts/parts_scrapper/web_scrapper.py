# -*- coding: utf-8 -*-
import requests
import json
import re

from lxml import html
from datetime import date
from logging.handlers import RotatingFileHandler


def boatsnet_manufacturers():
    page = requests.get(
        'http://www.boats.net/'
    )
    tree = html.fromstring(page.content)
    xpath_selector = """/html/body/div[7]/div[1]/div[2]/div/div/div/div/div/div[2]/div/div[1]//
        *[contains(@class,"manufacturers-thumbs")]/div/div/div/a"""

    return tree.xpath(xpath_selector)


# Scrap categories, years, models and parts from http://www.boats.net/
def boatsnet_scrapper():
    manufacturers = boatsnet_manufacturers()

    for manufacturer in manufacturers:
        img = manufacturer.xpath('img')[0]
        print(img.get('alt'))
        print(manufacturer.get('href'))
        print(manufacturer.xpath('img')[0].get('src'))


if __name__ == '__main__':
    boatsnet_scrapper()
