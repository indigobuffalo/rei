from typing import Dict, List

import asyncio

from dashboard.models.garage_sale import GarageSale
from dashboard.orms.rei import get_garage_sales, STORE_MAP


class REIPresenter:

    FILTERS_MAP = {
        'store': str
    }

    @staticmethod
    def _validate_stores(stores: List[str]):
        for store in stores:
            if store not in STORE_MAP:
                raise ValueError(f'Unrecognized REI location: {store}')

    @staticmethod
    def _present(garage_sales: List[GarageSale]) -> List[Dict]:
        def convert_to_json(garage_sale):
            return {
                'address': garage_sale.address,
                'date': garage_sale.date,
                'store': garage_sale.store,
                'phone': garage_sale.phone,
                'time': garage_sale.time,
                'url': garage_sale.url
            }
        return [convert_to_json(gs) for gs in garage_sales]

    def get_garage_sales(self, filters: Dict = None):
        stores = filters.get('stores')
        if stores:
            self._validate_stores(stores)

        garage_sales = asyncio.run(get_garage_sales(stores=stores))
        return self._present(garage_sales)

