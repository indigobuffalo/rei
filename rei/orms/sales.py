#! /usr/bin/env python
import re
import sys

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pprint import pprint
import time
from typing import List, Tuple

from rei.models.garage_sale import GarageSale


BASE_GS_URL = "https://www.rei.com/events/86150/members-only-garage-sale/"
STORE_MAP = {
    "berkeley": "269055",
    "concord":  "265816",
    "saratoga": "265826",
    "sf":       "266085",
}


class REIStoreORM:

    def __init__(self, name):
        self.name = name.lower()

    @staticmethod
    def scrub_key_val(key_and_val: List[str]) -> Tuple[str, str]:
        k, v = key_and_val
        k_scrubbed = k.replace('"', '').strip().title()
        v_scrubbed = v.replace('"', '').replace(',', '').strip().title()
        return k_scrubbed, v_scrubbed

    async def get_garage_sale_html_lines(self, session: aiohttp.ClientSession):
        resp = await session.get(BASE_GS_URL + STORE_MAP[self.name])
        content = await resp.content.read()
        text = BeautifulSoup(content, 'html.parser').get_text()
        return [ln.strip().lower() for ln in text.split('\n')]

    async def get_garage_sale(self, session: aiohttp.ClientSession) -> GarageSale:
        address = None
        phone = None
        date = None
        hours = None

        hours_pattern = re.compile('^[\d]{1,2}:[\d]{1,2}[a-zA-Z]{2}.[\d]{1,2}:[\d]{1,2}[a-zA-Z]{2}$')  # 8:00am-1:00pm
        date_pattern = re.compile('[a-zA-Z]+, [a-zA-Z]+ \d{1,2}, \d{4}')  # Saturday, February 08, 2020
        street_pattern = re.compile('\d+ .+,[\sa-zA-Z]+,\s*ca \d{5}')

        gs_html = await self.get_garage_sale_html_lines(session)
        for line in gs_html:
            if street_pattern.match(line):
                address = line
            if hours_pattern.match(line):
                hours = line.replace('–', '-')
            if date_pattern.match(line):
                date = line
            if "call us at" in line:
                phone = line.split("call us at")[1]

        return GarageSale(address=address, date=date, phone=phone, hours=hours)


async def get_garage_sales(stores: List[str] = None):
    stores = stores or list(STORE_MAP.keys())
    async with aiohttp.ClientSession() as session:
        tasks = []
        for store in stores:
            rso = REIStoreORM(store)
            tasks.append(rso.get_garage_sale(session))
        return await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    print(f"Started at {time.strftime('%X')}")
    stores = sys.argv[1:] if len(sys.argv) > 1 else list(STORE_MAP.keys())
    garage_sales = asyncio.run(get_garage_sales(stores))
    pprint([gs.to_json() for gs in garage_sales])
    print(f"Ended at {time.strftime('%X')}")

