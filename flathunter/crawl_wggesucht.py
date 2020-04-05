# coding= UTF-8

import logging
import re

import requests
from bs4 import BeautifulSoup


class CrawlWgGesucht:
    __log__ = logging.getLogger(__name__)
    URL_PATTERN = re.compile(r'https://www\.wg-gesucht\.de')

    def __init__(self):
        logging.getLogger("requests").setLevel(logging.WARNING)

    def get_results(self, search_url):
        self.__log__.debug("Got search URL %s" % search_url)

        # load page
        soup = self.get_page(search_url)
        
        # extract data
        entries = self.extract_data_v1(soup)

        return entries

    def get_page(self, search_url):
        resp = requests.get(search_url)
        if resp.status_code != 200:
            self.__log__.error("Got response (%i): %s" % (resp.status_code, resp.content))
        return BeautifulSoup(resp.content, 'lxml')

    def extract_data_v1(self, soup):
        ### get number of entries on first page
        offer_entries = soup.find_all('tr', class_="offer_list_item")
        self.__log__.info('Found offers: ' + str(len(offer_entries)))

        entries = []
        for offer in offer_entries[0:1]:
            id = int(offer.find('td', class_='asset_favourite')['data-ad_id'])
            rooms = offer.find('td', class_='ang_spalte_zimmer').find('span').get_text().strip()
            size = offer.find('td', class_='ang_spalte_groesse').find('span').get_text().strip()
            price = offer.find('td', class_='ang_spalte_miete').find('span').get_text().strip()
            url = 'https://www.wg-gesucht.de/' + offer.find('td', class_='ang_spalte_zimmer').a.get('href')
            availableFrom = offer.find('td', class_='ang_spalte_freiab').find('span').get_text().strip()

            details = {
                'id': id,
                'url': url,
                'title': "%s Zimmer ab dem %s" % (rooms, availableFrom),
                'price': price,
                'size': size,
                'rooms': rooms + " Zimmer",
                'address': url
            }
            entries.append(details)

        return entries

    def load_address(self, url):
        # extract address from expose itself
        r = requests.get(url)
        flat = BeautifulSoup(r.content, 'lxml')
        address = ' '.join(flat.find('div', {"class": "col-sm-4 mb10"}).find("a", {"href": "#"}).text.strip().split())
        return address