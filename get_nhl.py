import requests
from pprint import pprint

NHL = "https://statsapi.web.nhl.com/api/v1/schedule?startDate=2019-12-17&endDate=2019-12-17"

resp = requests.get(NHL).json()

import ipdb
ipdb.set_trace()

games= resp['dates'][0]['games']



