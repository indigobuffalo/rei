"""Model representing an rei store"""


class GarageSale:
    def __init__(self, address: str, date: str, phone: str, hours: str):
        self.address = address
        self.date = date
        self.phone = phone
        self.hours = hours
