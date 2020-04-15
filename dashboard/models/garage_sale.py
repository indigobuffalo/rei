"""Model representing an rei store"""
from datetime import datetime


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

    @property
    def hours(self):
        start = datetime.strftime(self.start, '%I:%M %p')
        end = datetime.strftime(self.end, '%I:%M %p')
        return f'{start} - {end}'

    @property
    def date(self):
        return datetime.strftime(self.start, '%B %d, %Y')


