"""Get the latest nhl stats

Usage:
  nhl.py <days>
  nhl.py --start=<start_date> --end=<end_date>

Examples:
  get_nhl.py --start 02-02 --end 02-04
  get_nhl.py --start 2019-04-11 --end 2019-05-12
  get_nhl.py 7 
    
Options:
  --days                  Days to collect stats for, counting back from today
  --start=<start_date>    Start date, in format %Y-%m-%d
  --end=<end_date>        End date, in format %Y-%m-%d
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
    return args['--start'], args['--end']


def parse_game_feed(game: Dict, teams: Dict) -> Dict:
    """"Parse game feed url from a game dictionary.
    
    The game feeds contain stats for the game. For example.
    you can search a game feed response for the string
    "scorer" to determine who scored in the game.
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

    games_per_team = rec_dd()
    for date in resp['dates']:
        for game in date['games']:
            games_per_team = parse_game_feed(game, games_per_team)
    games_per_team = dd_to_regular(games_per_team)
    pprint(games_per_team)
            
