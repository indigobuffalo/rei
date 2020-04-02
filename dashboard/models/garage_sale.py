"""Model representing an rei store"""
from datetime import datetime

'''
{'address': '1338 San Pablo Ave, Berkeley',
 'date': 'February 08, 2020',
 'store': 'Berkeley Rei',
 'phone': '(510) 527-4140',
 'time': '08:00 AM - 01:00 PM',
 'url': 'https://www.rei.com/events/86150/members-only-garage-sale/269055'}
'''


class GarageSale:
    def __init__(
            self,
            address: str,
            phone: str,
            start: datetime,
            end: datetime,
            store: str,
            url: str
    ):
        self.address = address
        self.phone = phone
        self.start = start
        self.end = end
        self.store = store
        self.url = url

