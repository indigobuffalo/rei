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
  --start=<start_date>     Start date, in format %Y-%m-%d.
  --end=<end_date>         End date, in format %Y-%m-%d.
  --year=<year>            Year of start and end dates, in format %Y.

"""
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
import pprint
from typing import Dict, Tuple, List
import pathlib

import asyncio
import aiohttp
import requests

import pytz
from pytz import timezone
from docopt import docopt

from dashboard.log_helper import setup_stream_logger

CURRENT_DIR = pathlib.Path(__file__).parent.absolute()
STATS_URL = 'https://statsapi.web.nhl.com'

LOGGER = setup_stream_logger()

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
    start, end = args['--start'], args['--end']
    if not all(re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', d) for d in [start, end]):
        raise ValueError('Start and end dates must be of format YYYY-MM-DD')
    return start, end


def parse_date_and_feed(game: Dict) -> Tuple[str, str]:
    """"Parse game feed url from a game dictionary.

    The game feed resource contains stats for the game.
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
        skaters[name_last_first]['games'] += 1
        stats = parse_skater_stats(info['stats']['skaterStats'])
        for stat in stats:
            skaters[name_last_first][stat[0]] += stat[1]
    if 'goalieStats' in info['stats']:
        goalies[name_last_first]['games'] += 1
        stats = parse_goalie_stats(info['stats']['goalieStats'])
        for stat in stats:
            goalies[name_last_first][stat[0]] += stat[1]
    return skaters, goalies


async def parse_stats(session: aiohttp.ClientSession, feed: str) -> Tuple[Dict, Dict]:
    skaters = defaultdict(lambda: defaultdict(int))
    goalies = defaultdict(lambda: defaultdict(int))
    resp = await session.get(feed)
    resp_json = await resp.json()
    box = resp_json['liveData']['boxscore']['teams']
    home_players = box['home']['players']
    away_players = box['away']['players']
    for player, info in home_players.items():
        skaters, goalies = parse_player_stats(info, skaters, goalies)
    for player, info in away_players.items():
        skaters, goalies = parse_player_stats(info, skaters, goalies)
    return dd_to_regular(skaters), dd_to_regular(goalies)


async def fetch_game_stats_concurrently(game_feeds: List[str]) -> List[Tuple[Dict, Dict]]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for feed in game_feeds:
            tasks.append(parse_stats(session=session, feed=feed))
        game_stats = await asyncio.gather(*tasks, return_exceptions=True)
        return game_stats


def main(args):
    start, end = get_start_and_end_dates(args)

    session = requests.session()
    stats_url = f"{STATS_URL}/api/v1/schedule?startDate={start}&endDate={end}"
    stats_resp = session.get(stats_url).json()

    feeds_by_date = defaultdict(set)
    for date in stats_resp['dates']:
        LOGGER.info(f'Collecting stats for {date["totalGames"]} games on {date["date"]}')
        for game in date['games']:
            date, feed = parse_date_and_feed(game)
            feeds_by_date[date].add(feed)

    skater_stats_cumulative = {}
    goalie_stats_cumulative = {}

    game_feeds = [f for feeds in feeds_by_date.values() for f in feeds]
    game_stats = asyncio.run(fetch_game_stats_concurrently(game_feeds))

    for skaters, goalies in game_stats:
        for skater, stats in skaters.items():
            if skater in skater_stats_cumulative:
                for stat in stats:
                    skater_stats_cumulative[skater][stat] += stats[stat]
            else:
                skater_stats_cumulative[skater] = stats
        for goalie, stats in goalies.items():
            if goalie in goalie_stats_cumulative:
                for stat in stats:
                    goalie_stats_cumulative[goalie][stat] += stats[stat]
            else:
                goalie_stats_cumulative[goalie] = stats

    output_file = os.path.join(CURRENT_DIR, f'{start}_to_{end}.txt')
    with open(os.path.join(CURRENT_DIR, output_file), 'w') as f:
        f.write(pprint.pformat(skater_stats_cumulative))
        f.write(pprint.pformat(goalie_stats_cumulative))


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
