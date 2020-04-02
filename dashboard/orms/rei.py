#! /Users/Akerson/.virtualenvs/dashboard-0jca69GK/bin/python

import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from typing import Dict, List, Tuple

BASE_GS_URL = "https://www.rei.com/events/86150/members-only-garage-sale/"
GS_BLOB_START = '"name" : "members only garage sale!",'
GS_BLOB_END = u'"addresscountry" : "us"'
KEY_DETAILS = [
    'name',
    'startdate',
    'enddate',
    'telephone',
    'url',
    'streetaddress',
    'addresslocality',
]
STORE_MAP = {
    "berkeley": "269055",
    "concord":  "265816",
    "saratoga": "265826",
    "sf":       "266085",
}


class REIStoreORM:

    def __init__(self, store):
        self.store = store.lower()
        resp = requests.get(BASE_GS_URL + STORE_MAP[self.store])
        text = BeautifulSoup(resp.content, 'html.parser').get_text()
        self.resp_lines = [ln.strip().lower() for ln in text.split('\n')]

    @staticmethod
    def prettify(garage_sale: Dict) -> Dict:
        street, city = garage_sale.pop('Streetaddress'), garage_sale.pop('Addresslocality')
        garage_sale['address'] = f"{street.title()}, {city.title()}"

        start_date, start_time_24 = garage_sale.pop('Startdate').split('T')
        end_date, end_time_24 = garage_sale.pop('Enddate').split('T')
        start_time = datetime.strptime(start_time_24.split('-')[0], '%H:%M').strftime('%I:%M %p')
        end_time = datetime.strptime(end_time_24.split('-')[0], '%H:%M').strftime('%I:%M %p')
        garage_sale['date'] = datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')
        garage_sale['time'] = f'{start_time} - {end_time}'

        phone = garage_sale.pop('Telephone')
        garage_sale['phone'] = f'({phone[2:5]}) {phone[5:8]}-{phone[8:13]}'

        url = garage_sale.pop('Url')
        garage_sale['url'] = url.lower()

        name = garage_sale.pop('Name')
        garage_sale['name'] = name

        return garage_sale

    @staticmethod
    def scrub_key_val(key_and_val: List[str]) -> Tuple[str, str]:
        k, v = key_and_val
        k_scrubbed = k.replace('"', '').strip().title()
        v_scrubbed = v.replace('"', '').replace(',', '').strip().title()
        return k_scrubbed, v_scrubbed

    def parse_garage_sale(self):
        garage_sale = {}
        found_garage_sale = False

        for line in self.resp_lines:
            if found_garage_sale:
                if any(detail in line for detail in KEY_DETAILS):
                    k, v = self.scrub_key_val(line.split(':', 1))
                    garage_sale[k] = v
                if line == GS_BLOB_END:
                    break
            if line == GS_BLOB_START:
                found_garage_sale = True
        return garage_sale

    def get_garage_sale(self) -> Dict:
        garage_sale = self.parse_garage_sale()
        return self.prettify(garage_sale)


if __name__ == "__main__":
    stores = sys.argv[1:] if len(sys.argv) > 1 else list(STORE_MAP.keys())

    for store in stores:
        print("\n")
        rso = REIStoreORM(store)
        details = rso.get_garage_sale()
        pprint(details)

