from typing import Dict, List
from datetime import datetime

import asyncio

from dashboard.models.garage_sale import GarageSale
from dashboard.orms.rei import get_garage_sales, STORE_MAP


class REIPresenter:

    @staticmethod
    def _present(garage_sale: GarageSale) -> Dict:
        start = datetime.strftime(garage_sale.start, '%I:%M %p')
        end = datetime.strftime(garage_sale.end, '%I:%M %p')
        return {
            'address': garage_sale.address,
            'phone': garage_sale.phone,
            'hours': f'{start} - {end}',
            'store': garage_sale.store,
            'url': garage_sale.url
        }

    def get_garage_sales(self):
        garage_sales = asyncio.run(get_garage_sales())
        return [self._present(gs) for gs in garage_sales]

