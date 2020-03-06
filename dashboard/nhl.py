"""Get the latest nhl stats

Usage:
  nhl.py <days> [options]
  nhl.py --start=<start_date> --end=<end_date> [options]

Examples:
  get_nhl.py --start 02-02 --end 02-04
  get_nhl.py --start 2019-04-11 --end 2019-05-12
  get_nhl.py 7 
    
Options:
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

from dashboard.log_helper import setup_file_logger, setup_stream_logger

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
STATS_URL = 'https://statsapi.web.nhl.com'


def dd_to_regular(d):
    "Converts a defaultdict of defaultdicts to a dict of dicts"
    if isinstance(d, defaultdict):
        d = {k: dd_to_regular(v) for k, v in d.items()}
    return d


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


def parse_skater_stats(stats):
    goals = stats['goals']
    assists = stats['assists']
    shots = stats['shots']
    blocks = stats['blocked']
    hits = stats['hits']
    plus_minus = stats['plusMinus']
    return [
        ('goals', goals),
        ('assists', assists),
        ('shots', shots),
        ('blocks', blocks),
        ('hits', hits),
        ('+/-', plus_minus)
    ]    
    

def parse_stats(feed: Dict, players: Dict) -> Dict:
    resp = requests.get(feed).json()
    box = resp['liveData']['boxscore']['teams']
    home_players = box['home']['players']
    away_players = box['away']['players']

    for player, info in home_players.items():
        if not info['stats'].get('skaterStats'):
            print("Goalie stats")
            break
        name = info['person']['fullName']
        stats = info['stats']['skaterStats']
        
        print(parse_skater_stats(stats))
        for stat in parse_skater_stats(stats):
            players[name][stat[0]] += stat[1]

    for player, stats in away_players.items():
        if not info['stats'].get('skaterStats'):
            print("Goalie stats")
            break
        name = info['person']['fullName']
        stats = info['stats']['skaterStats']
        
        print(parse_skater_stats(stats))
        for stat in parse_skater_stats(stats):
            players[name][stat[0]] += stat[1]

    return players


def main(args):
    log_level, log_file  = args['--log-level'], args['--output']
    stream_logger = setup_stream_logger(log_level)
    file_logger = setup_file_logger(log_level, log_file)

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
    print(game_feeds)

    players = defaultdict(lambda: defaultdict(int))
    for date, feeds in game_feeds.items():
        players = parse_stats(feeds.pop(), players)

    pprint(dd_to_regular(players))


if __name__ == "__main__":
    args = docopt(__doc__)
    main(args)
   
