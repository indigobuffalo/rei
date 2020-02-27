"""Get the latest nhl stats

Usage:
  nhl.py <days> [options]
  nhl.py --start=<start_date> --end=<end_date> [options]

Examples:
  get_nhl.py --start 02-02 --end 02-04
  get_nhl.py --start 2019-04-11 --end 2019-05-12
  get_nhl.py 7 
    
Options:
  --days                  Days to collect stats for, counting back 
                          from, and including, today.
  --start=<start_date>    Start date, in format %Y-%m-%d.
  --end=<end_date>        End date, in format %Y-%m-%d.
  --year=<year>           Year of start and end dates, in format %Y.
  --log-level=<level>     The log level to set the logger to [default: INFO]
  --output=<file>         Name of the output log file [default: output.log]

"""

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pprint import pprint
from typing import Dict, Tuple
import requests
import os

import pytz
from pytz import timezone
from docopt import docopt

from log_helper import setup_file_logger, setup_stream_logger

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
STATS_URL = 'https://statsapi.web.nhl.com'


def get_start_and_end_dates(args: Dict) -> Tuple[str, str]:
    """Parse start and end dates from a docopts.Dict"""
    days = int(args['<days>']) if args['<days>'] else None
    if days is not None:
        if days == 0:
            raise ValueError("Days must be a positive integer")
        today = date.today()
        start = (today - timedelta(days=days-1)).strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
        return start, end
    return args['--start'], args['--end']


def parse_date_and_feed(game: Dict) -> Tuple[str, str]:
    """"Parse game feed url from a game dictionary.
    
    The game feed contains stats for the game.
    """
    datetime_utc_naive = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ') 
    datetime_utc = pytz.utc.localize(datetime_utc_naive)
    datetime_pacific = datetime_utc.astimezone(timezone('US/Pacific'))
    date = datetime.strftime(datetime_pacific, '%Y-%m-%d')
    return (date, STATS_URL + game['link'])


def parse_stats(feed: Dict) -> Dict:
    stats = {
        'goals': {},
        'assists': {},
        'shots': {},
        'blocks': {},
        'hits': {},
        'plus_minus': {},
    }
    resp = requests.get(feed).json()
    box = resp['liveData']['boxscore']['teams']
    home_players = box['home']['players']
    away_players = box['away']['players']

    for player, stats in home_players.items():
        file_logger.debug((player))
        file_logger.info((stats))
        break
    for player, stats in away_players.items():
        file_logger.debug((player))
        file_logger.info((stats))
        break


if __name__ == "__main__":
    args = docopt(__doc__)

    log_level = args['--log-level']
    output_file = args['--output']
   

    stream_logger = setup_stream_logger(log_level)
    file_logger = setup_file_logger(log_level, output_file)

    start, end = get_start_and_end_dates(args)
    stream_logger.info((f"Retriving stats for games played between '{start}' and '{end}'."))
    stats_url = f"{STATS_URL}/api/v1/schedule?startDate={start}&endDate={end}"
    resp = requests.get(stats_url).json()

    game_feeds = defaultdict(set)
    for date in resp['dates']:
        for game in date['games']:
            date, feed = parse_date_and_feed(game)
            game_feeds[date].add(feed)
    game_feeds = dict(game_feeds)

    for date, feeds in game_feeds.items():
        parse_stats(feeds.pop())

