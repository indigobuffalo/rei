#! /Users/Akerson/.virtualenvs/dashboard-0jca69GK/bin/python

import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from typing import List, Tuple

from dashboard.models.garage_sale import GarageSale

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

    def get_garage_sale(self) -> GarageSale:
        gs_html = self.parse_garage_sale()

        street, city = gs_html.pop('Streetaddress'), gs_html.pop('Addresslocality')
        address = f"{street.title()}, {city.title()}"

        phone = gs_html.pop('Telephone')
        phone_fmt = f'({phone[2:5]}) {phone[5:8]}-{phone[8:13]}'

        start = gs_html.pop('Startdate')
        start_datetime = datetime.strptime(start, '%Y-%m-%dT%H:%M')

        end = gs_html.pop('Enddate')
        end_datetime = datetime.strptime(end, '%Y-%m-%dT%H:%M')

        return GarageSale(
            address=address,
            phone=phone_fmt,
            start=start_datetime,
            end=end_datetime,
            store=gs_html['Name'].lower().title().replace('Rei', 'REI'),
            url=gs_html['Url'].lower()
        )


if __name__ == "__main__":
    stores = sys.argv[1:] if len(sys.argv) > 1 else list(STORE_MAP.keys())

    for store in stores:
        print("\n")
        rso = REIStoreORM(store)
        garage_sale = rso.get_garage_sale().to_json()
        pprint(garage_sale)

