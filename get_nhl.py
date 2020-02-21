"""Get the latest nhl stats

Usage:
  get_nhl.py --days
  get_nhl.py --start=<start_date> --end=<end_date> [--year=<year>]

Examples:
  get_nhl.py --start 02-02 --end 02-04
  get_nhl.py --start 04-11 --end 05-12 --year 2019
  get_nhl.py 7 
    
Options:
  --days                  Days ago from which to start collecting stats
  --start=<start_date>    Start date, in format %m-%d
  --end=<end_date>        End date, in format %m-%d
  --year=<year>           Year of start and end dates, in format %Y

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
    start_mm_dd = args['--start']
    end_mm_dd = args['--end']
    year = args['--year'] if args['--year'] else '2020'

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



