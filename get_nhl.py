"""Get the latest nhl stats

Usage:
  get_nhl.py START END [YEAR]

"""

import requests
from pprint import pprint
from datetime import datetime
from typing import Dict

from docopt import docopt


def get_games_played(resp: Dict):
    return resp['dates'][0]['games'] 


if __name__ == "__main__":
    args = docopt(__doc__)
    start_mm_dd = args['START']
    end_mm_dd = args['END']
    year = args['YEAR'] if args['YEAR'] is not None else '2020'
    
    # ensure date args formated properly
    datetime.strptime(start_mm_dd, '%m-%d')
    datetime.strptime(end_mm_dd, '%m-%d')
    datetime.strptime(year, '%Y')

    stats_url = f"https://statsapi.web.nhl.com/api/v1/schedule?startDate={year}-{start_mm_dd}&endDate={year}-{end_mm_dd}"
    resp = requests.get(stats_url).json()

    import ipdb
    ipdb.set_trace()


    games_first_date_in_range = resp['dates'][0]['games']
    games_second_date_in_range = resp['dates'][1]['games']
    games_second_third_in_range = resp['dates'][2]['games']



