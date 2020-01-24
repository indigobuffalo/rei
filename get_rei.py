import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.rei.com/stores/{store}.html"
BASE_URL_2 = "https://www.rei.com/events/86150/members-only-garage-sale/"

STORE_MAP = {
    "berkeley": "269055",
    "concord":  "265815",
    "saratoga": "265834",
    "sf":       "266084",
}

resp = requests.get(BASE_URL.format(store='saratoga'))
soup = BeautifulSoup(resp.content, 'html.parser')
text = soup.get_text()
text_lines = text.split('\n')

times = []
garage_sales = []
for idx, line in enumerate(text.split('\n')):
    if '9:30' in line:
        times.append((idx,line))
    if 'garage sale' in line.strip().lower():
        garage_sales.append(line)


with open('yooo.txt', 'w') as tf:
    tf.write(str(resp.content))


import ipdb
ipdb.set_trace()


