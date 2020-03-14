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
from typing import Dict, Tuple
from pathlib import Path

import requests

import pytz
from pytz import timezone
from docopt import docopt


CURRENT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = CURRENT_DIR.joinpath('..')
OUTPUT_DIR = PROJECT_DIR.joinpath('output')
STATS_URL = 'https://statsapi.web.nhl.com'


def dd_to_regular(d):
    """Converts a defaultdict of defaultdicts to a dict of dicts"""
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


class StatsScraper:

    def __init__(self, base_stats_url, start_date, end_date):
        self.stats_url = f"{base_stats_url}/api/v1/schedule?startDate={start_date}&endDate={end_date}"
        self.output_file = os.path.join(OUTPUT_DIR, f'stats_{start_date}_to_{end_date}.txt')

        self.session = requests.Session()

        self.skater_stats = {}
        self.goalie_stats = {}
        self.game_feeds = None

    @staticmethod
    def parse_date_and_feed(game: Dict) -> Tuple[str, str]:
        """"Parse game feed url from a game dictionary.

        The game feed contains stats for the game.
        """
        datetime_utc_naive = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ')
        datetime_utc = pytz.utc.localize(datetime_utc_naive)
        datetime_pacific = datetime_utc.astimezone(timezone('US/Pacific'))
        game_date = datetime.strftime(datetime_pacific, '%Y-%m-%d')
        return game_date, STATS_URL + game['link']

    @staticmethod
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

    @staticmethod
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

    def parse_player_stats(self, info, skaters, goalies):
        name = info['person']['fullName']
        first, last = name.split(" ", 1)
        name_last_first = f'{last}, {first}'
        if 'skaterStats' in info['stats']:
            skaters[name_last_first]['games'] += 1
            stats = self.parse_skater_stats(info['stats']['skaterStats'])
            for stat in stats:
                skaters[name_last_first][stat[0]] += stat[1]
        if 'goalieStats' in info['stats']:
            goalies[name_last_first]['games'] += 1
            stats = self.parse_goalie_stats(info['stats']['goalieStats'])
            for stat in stats:
                goalies[name_last_first][stat[0]] += stat[1]
        return skaters, goalies

    def parse_stats(self, feed: Dict) -> Tuple[Dict, Dict]:
        skaters = defaultdict(lambda: defaultdict(int))
        goalies = defaultdict(lambda: defaultdict(int))
        resp = self.session.get(feed).json()
        box = resp['liveData']['boxscore']['teams']
        home_players = box['home']['players']
        away_players = box['away']['players']
        for player, info in home_players.items():
            skaters, goalies = self.parse_player_stats(info, skaters, goalies)
        for player, info in away_players.items():
            skaters, goalies = self.parse_player_stats(info, skaters, goalies)
        return dd_to_regular(skaters), dd_to_regular(goalies)

    def get_game_feeds(self):
        stats_resp = self.session.get(self.stats_url).json()
        game_feeds = defaultdict(set)
        for date in stats_resp['dates']:
            print(f'Collecting stats for {date["totalGames"]} games on {date["date"]}')
            for game in date['games']:
                date, feed = self.parse_date_and_feed(game)
                game_feeds[date].add(feed)
        self.game_feeds = dict(game_feeds)

    def get_stats(self):
        for date, feeds in self.game_feeds.items():
            for game_feed in feeds:
                skaters, goalies = self.parse_stats(game_feed)
                for skater, stats in skaters.items():
                    if skater in self.skater_stats:
                        for stat in stats:
                            self.skater_stats[skater][stat] += stats[stat]
                    else:
                        self.skater_stats[skater] = stats
                for goalie, stats in goalies.items():
                    if goalie in self.goalie_stats:
                        for stat in stats:
                            self.goalie_stats[goalie][stat] += stats[stat]
                    else:
                        self.goalie_stats[goalie] = stats

    def write_stats(self):
        with open(self.output_file, 'w') as f:
            f.write(pprint.pformat(self.skater_stats))
            f.write(pprint.pformat(self.goalie_stats))


def main(args):
    start, end = get_start_and_end_dates(args)

    if not OUTPUT_DIR.is_dir():
        Path.mkdir(OUTPUT_DIR)

    scraper = StatsScraper(STATS_URL, start, end)
    scraper.get_game_feeds()
    scraper.get_stats()
    scraper.write_stats()


if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
