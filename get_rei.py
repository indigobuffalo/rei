import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from typing import Dict, List, Tuple, Union

STORE_MAP = {
    "berkeley": "269055",
    "concord":  "265815",
    "saratoga": "265834",
    "sf":       "266084",
}

BASE_URL = "https://www.rei.com/events/86150/members-only-garage-sale/"

GS_BLOB_START = '"name" : "members only garage sale!",'
GS_BLOB_END = u'"addresscountry" : "us"'

def contains_key_detail(line):
    key_details = [
        'name',
        'startdate',
        'enddate',
        'telephone',
        'url',
        'streetaddress',
        'addresslocality',
    ]
    return any(x in line for x in key_details)

def prettify_dict(garage_sale: Dict) -> Dict:
    street, city = garage_sale.pop('Streetaddress'), garage_sale.pop('Addresslocality')
    garage_sale['address'] = f"{street.title()}, {city.title()}"

    start_date, start_time_24H = garage_sale.pop('Startdate').split('T')
    end_date, end_time_24H = garage_sale.pop('Enddate').split('T')
    start_time = datetime.strptime(start_time_24H.split('-')[0], '%H:%M').strftime('%I:%M %p')
    end_time = datetime.strptime(end_time_24H.split('-')[0], '%H:%M').strftime('%I:%M %p')
    garage_sale['date'] = datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')
    garage_sale['time'] = f'{start_time} - {end_time}'

    phone = garage_sale.pop('Telephone')
    garage_sale['phone'] = f'({phone[2:5]}) {phone[5:8]}-{phone[8:13]}'

    url = garage_sale.pop('Url')
    garage_sale['url'] = url.lower()

    name = garage_sale.pop('Name')
    garage_sale['name'] = name

    return garage_sale

def scrub_key_val(key_and_val: List[str]) -> Tuple[str, str]:
    k, v = key_and_val
    k_scrubbed = k.replace('"', '').strip().title()
    v_scrubbed = v.replace('"', '').replace(',', '').strip().title()

    return k_scrubbed, v_scrubbed

def get_response_as_lines_of_text(store: str) -> List[str]:
    resp = requests.get(BASE_URL + STORE_MAP[store.lower()])
    resp.raise_for_status()
    text = BeautifulSoup(resp.content, 'html.parser').get_text()
    return [line.strip().lower() for line in text.split('\n')]

def get_garage_sale_dates(store) -> Dict:
    text_lines = get_response_as_lines_of_text(store)
    garage_sale = {}
    found_garage_sale = False
    for line in text_lines:
        if found_garage_sale:
            if contains_key_detail(line):
                k, v = scrub_key_val(line.split(':', 1))
                garage_sale[k] = v
            if line == GS_BLOB_END:
                break
        if line == GS_BLOB_START:
            found_garage_sale = True
    return prettify_dict(garage_sale)

def get_garage_sale_dates_debug(store) -> List[str]:
    text_lines = get_response_as_lines_of_text(store)
    garage_sale = []
    found_garage_sale = False
    for line in text_lines:
        if found_garage_sale:
            garage_sale.append(line)
            if line == GS_BLOB_END:
                break
        if line == GS_BLOB_START:
            found_garage_sale = True
    return garage_sale

def main(stores: List, debug:bool = False) -> None:
    for store in stores:
        print("\n")
        if debug:
            details = get_garage_sale_dates_debug(store)
        else:
            details = get_garage_sale_dates(store)
        pprint(details)


if __name__ == "__main__":
    debug =  "debug" in sys.argv
    if debug:
        sys.argv.remove("debug")
    stores = sys.argv[1:] if len(sys.argv) > 1 else list(STORE_MAP.keys())
    main(stores, debug=debug)

