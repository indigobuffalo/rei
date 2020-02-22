"""Get the latest nhl stats

Usage:
  nhl.py <days>
  nhl.py --start=<start_date> --end=<end_date> [--year=<year>]

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

STATS_URL = 'https://statsapi.web.nhl.com'


def rec_dd():
    """Return a recursive defaultdict of defaultdicts"""
    return defaultdict(rec_dd)

def dd_to_regular(d):
    "Convert a defaultdict of defaultdicts to a dict of dicts"
    if isinstance(d, defaultdict):
        d = {k: dd_to_regular(v) for k, v in d.items()}
    return d

def get_start_and_end_dates(args: Dict) -> Tuple[str, str]:
    """Parse start and end dates from a docopts.Dict"""
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


def parse_game_feeds(game: Dict, teams: Dict) -> Dict:
    """"Parse game feed urls per team from a response date.
    The game feeds contain stats for the game.  

    For example, you can search a game feed response for the 
    string "scorer" to determine who scored in the game.
    """
    home = game['teams']['home']['team']['name']
    away = game['teams']['away']['team']['name']

    datetime_utc_naive = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ') 
    datetime_utc = pytz.utc.localize(datetime_utc_naive)
    datetime_pacific = datetime_utc.astimezone(timezone('US/Pacific'))
    date = datetime.strftime(datetime_pacific, '%Y-%m-%d')

    teams[home]['games'][f"{date} vs {away}"] = STATS_URL + game['link']
    teams[away]['games'][f"{date} vs {home}"] = STATS_URL + game['link']
    
    return teams

if __name__ == "__main__":
    args = docopt(__doc__)
    start, end = get_start_and_end_dates(args)
    stats_url = f"{STATS_URL}/api/v1/schedule?startDate={start}&endDate={end}"
    resp = requests.get(stats_url).json()

    teams = rec_dd()
    for date in resp['dates']:
        for game in date['games']:
            teams = parse_game_feeds(game, teams)
    teams = dd_to_regular(teams)
    pprint(teams)
            
