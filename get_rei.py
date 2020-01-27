"""
Working for saratoga but not others
"""
import sys
from unicodedata import normalize

import requests
from bs4 import BeautifulSoup
from pprint import pprint

BASE_URL = "https://www.rei.com/stores/{store}.html"
BASE_URL_2 = "https://www.rei.com/events/86150/members-only-garage-sale/"

GS_BLOB_START = '"name" : "members only garage sale!",'
GS_BLOB_END = u'"addresscountry" : "us"'

STORE_MAP = {
    "berkeley": "269055",
    "concord":  "265815",
    "saratoga": "265834",
    "sf":       "266084",
}


def contains_key_detail(line):
    return any(x in line for x in ['startdate', 'enddate', 'telephone'])

def get_garage_sale_dates(store):
    resp = requests.get(BASE_URL_2 + STORE_MAP[store])
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, 'html.parser')
    text = soup.get_text()
    text_lines = [line.strip().lower() for line in text.split('\n')]

    garage_sale = []
    found_garage_sale = False
    for line in text_lines:
        if line == GS_BLOB_START:
            found_garage_sale = True
        if found_garage_sale: 
            if contains_key_detail(line):
                garage_sale.append(line)
            if line == GS_BLOB_END:
                break

    return garage_sale

for store in sys.argv[1:]:
  print(f"Getting garage sale info for {store}...\n")
  details = get_garage_sale_dates(store)
  pprint(details)
  print("\n")

