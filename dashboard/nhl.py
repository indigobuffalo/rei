#! /Users/Akerson/.virtualenvs/dashboard-0jca69GK/bin/python

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
    game_date = datetime.strftime(datetime_pacific, '%Y-%m-%d')
    return game_date, STATS_URL + game['link']


def parse_skater_stats(stats):
    assists = stats['assists']
    blocks = stats['blocked']
    hits = stats['hits']
    goals = stats['goals']
    plus_minus = stats['plusMinus']
    shots = stats['shots']
    return [
        ('goals', goals),
        ('assists', assists),
        ('shots', shots),
        ('blocks', blocks),
        ('hits', hits),
        ('+/-', plus_minus)
    ]


def parse_goalie_stats(stats):
    assists = stats['assists']
    goals = stats['goals']
    saves = stats['saves']
    shots = stats['shots']
    shutout = 1 if (shots == saves) and (shots > 0) else 0
    return [
        ('assists', assists),
        ('goals', goals),
        ('saves', saves),
        ('shots', shots),
        ('shutout', shutout)
    ]


def parse_player_stats(info, skaters, goalies):
    name = info['person']['fullName']
    first, last = name.split(" ", 1)
    name_last_first = f'{last}, {first}'
    if 'skaterStats' in info['stats']:
        stats = parse_skater_stats(info['stats']['skaterStats'])
        for stat in stats:
            skaters[name_last_first][stat[0]] += stat[1]
    if 'goalieStats' in info['stats']:
        stats = parse_goalie_stats(info['stats']['goalieStats'])
        for stat in stats:
            goalies[name_last_first][stat[0]] += stat[1]
    return skaters, goalies


def parse_stats(feed: Dict, skaters: Dict, goalies: Dict) -> Tuple[Dict, Dict]:
    resp = requests.get(feed).json()
    box = resp['liveData']['boxscore']['teams']
    home_players = box['home']['players']
    away_players = box['away']['players']
    for player, info in home_players.items():
        skaters, goalies = parse_player_stats(info, skaters, goalies)
    for player, info in away_players.items():
        skaters, goalies = parse_player_stats(info, skaters, goalies)
    return skaters, goalies


def main(args):
    start, end = get_start_and_end_dates(args)
    stats_url = f"{STATS_URL}/api/v1/schedule?startDate={start}&endDate={end}"
    resp = requests.get(stats_url).json()

    game_feeds = defaultdict(set)
    for date in resp['dates']:
        print(f'See {date["totalGames"]} games on {date["date"]}')
        for game in date['games']:
            date, feed = parse_date_and_feed(game)
            game_feeds[date].add(feed)
    game_feeds = dict(game_feeds)

    skaters = defaultdict(lambda: defaultdict(int))
    goalies = defaultdict(lambda: defaultdict(int))
    for date, feeds in game_feeds.items():
        skaters, goalies = parse_stats(feeds.pop(), skaters, goalies)

    print(f'Collected stats from {start} to {end}')
    print(f'Game feeds: {len(game_feeds)}')
    print(f'Skaters: {len(skaters)}')
    print(f'Goalies: {len(goalies)}')

    print('\n--------------')
    print('Skater stats:')
    print('--------------\n')
    pprint(dd_to_regular(skaters))
    print('\n--------------')
    print('Goalie stats:')
    print('--------------\n')
    pprint(dd_to_regular(goalies))


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
