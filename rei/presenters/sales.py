from typing import Dict
from datetime import datetime

import asyncio

from rei.models.garage_sale import GarageSale
from rei.orms.sales import get_garage_sales


class SalesPresenter:

    @staticmethod
    def _present(sale: Dict) -> Dict:
        presented = {}
        for k, v in sale.items():
            if not v:
                presented[k] = v
                continue
            if k == 'hours':
                v = v.upper()
            else:
                v = v.title()
            presented[k] = v
        return presented

    def get_garage_sales(self):
        garage_sales = asyncio.run(get_garage_sales())
        return [self._present(gs.__dict__) for gs in garage_sales]
