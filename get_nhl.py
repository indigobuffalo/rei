"""Get the latest nhl stats

Usage:
  get_nhl.py <days>
  get_nhl.py --start=<start_date> --end=<end_date> [--year=<year>]

Examples:
  get_nhl.py --start 02-02 --end 02-04
  get_nhl.py --start 04-11 --end 05-12 --year 2019
  get_nhl.py 7 
    
Options:
  --days                  Days to collect stats for, counting back from today
  --start=<start_date>    Start date, in format %m-%d
  --end=<end_date>        End date, in format %m-%d
  --year=<year>           Year of start and end dates, in format %Y

"""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pprint import pprint
from typing import Dict, Tuple
import requests

import pytz
from pytz import timezone
from docopt import docopt

STATS_URL = 'https://statsapi.web.nhl.com/api/v1/schedule'


def rec_dd():
    """Returns a recursive defaultdict of defaultdicts"""
    return defaultdict(rec_dd)

def dd_to_regular(d):
    "Converts a defaultdict of defaultdicts to a dict of dicts"
    if isinstance(d, defaultdict):
        d = {k: dd_to_regular(v) for k, v in d.items()}
    return d

def get_start_and_end_dates(args: Dict) -> Tuple[str, str]:
    days = args.get('<days>')
    if days:
        today = date.today()
        start = (today - timedelta(days=int(days)-1)).strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        return start, end
    year = args.get('--year') or date.today().year
    start = datetime.strptime(f'{year}-{args["--start"]}', '%Y-%m-%d')
    end = datetime.strptime(f'{year}-{args["--end"]}', '%Y-%m-%d')
    return start, end


def parse_game(game: Dict, teams: Dict) -> Dict:
    datetime_utc_naive = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ') 
    datetime_utc = pytz.utc.localize(datetime_utc_naive)
    datetime_pacific = datetime_utc.astimezone(timezone('US/Pacific'))
    date = datetime.strftime(datetime_pacific, '%Y-%m-%d')


    home = game['teams']['home']['team']['name']
    away = game['teams']['away']['team']['name']

    teams[home]['games'][date] = game['link']
    teams[away]['games'][date] = game['link']
    
    return teams

if __name__ == "__main__":
    args = docopt(__doc__)
    start, end = get_start_and_end_dates(args)
    stats_url = f"{STATS_URL}?startDate={start}&endDate={end}"
    resp = requests.get(stats_url).json()

    teams = rec_dd()
    for date in resp['dates']:
        for game in date['games']:
            teams = parse_game(game, teams)
    pprint(dd_to_regular(teams))
            
