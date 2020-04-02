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
import json
import time
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Tuple

import aiohttp
import asyncio
import requests

import pytz
from pytz import timezone
from docopt import docopt

from dashboard.log_helper import setup_stream_logger


LOGGER = setup_stream_logger()


def dd_to_regular(d):
    """Converts a defaultdict of defaultdicts to a dict of dicts"""
    if isinstance(d, defaultdict):
        d = {k: dd_to_regular(v) for k, v in d.items()}
    return d


class StatsScraper:

    def __init__(self, start_date, end_date):
        self.base_stats_url = 'https://statsapi.web.nhl.com'

        self.start_date = start_date
        self.end_date = end_date
        self.game_feeds = None
        self.game_stats = None

    @staticmethod
    def get_start_and_end_dates(args: Dict) -> Tuple[str, str]:
        """Parse start and end dates from a docopts.Dict"""
        days = int(args['<days>']) if args['<days>'] else None
        if days is not None:
            if days == 0:
                raise ValueError("Days must be a positive integer")
            end = date.today()
            start = (end - timedelta(days=days-1))
        else:
            start = datetime.strptime(args['--start'], '%Y-%m-%d')
            end = datetime.strptime(args['--end'], '%Y-%m-%d')

        if start > end:
            raise ValueError('Start date cannot be greater than end date')

        return datetime.strftime(start, '%Y-%m-%d'), datetime.strftime(end, '%Y-%m-%d')

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
        win = 1 if stats['decision'].lower() == 'w' else 0
        loss = 1 if stats['decision'].lower() == 'l' else 0
        return [
            ('assists', assists),
            ('goals', goals),
            ('loss', loss),
            ('saves', saves),
            ('shots', shots),
            ('shutout', shutout),
            ('win', win)
        ]

    def parse_date_and_feed(self, game: Dict) -> Tuple[str, str]:
        """"Parse game feed url from a game dictionary.

        The game feed resource contains stats for the game.
        """
        datetime_utc_naive = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ')
        datetime_utc = pytz.utc.localize(datetime_utc_naive)
        datetime_pacific = datetime_utc.astimezone(timezone('US/Pacific'))
        game_date = datetime.strftime(datetime_pacific, '%Y-%m-%d')
        return game_date, self.base_stats_url + game['link']

    def parse_player_stats(self, info, skaters, goalies):
        name = info['person']['fullName']
        first, last = name.split(" ", 1)
        name = f'{last}, {first}'

        skater_stats = info['stats'].get('skaterStats')
        goalie_stats = info['stats'].get('goalieStats')

        if skater_stats:
            skater = skaters[name]
            skater['games'] += 1
            stats = self.parse_skater_stats(skater_stats)
            for stat in stats:
                skater[stat[0]] += stat[1]

        if goalie_stats:
            goalie = goalies[name]
            goalie['games'] += 1
            stats = self.parse_goalie_stats(goalie_stats)
            for stat in stats:
                goalie[stat[0]] += stat[1]

        return skaters, goalies

    async def parse_game_stats(self, game_feed: str, session: aiohttp.ClientSession) -> Tuple[Dict, Dict]:
        skaters = defaultdict(lambda: defaultdict(int))
        goalies = defaultdict(lambda: defaultdict(int))
        resp = await session.get(game_feed)
        resp_json = await resp.json()
        box = resp_json['liveData']['boxscore']['teams']
        home_players = box['home']['players']
        away_players = box['away']['players']
        for player, info in home_players.items():
            skaters, goalies = self.parse_player_stats(info, skaters, goalies)
        for player, info in away_players.items():
            skaters, goalies = self.parse_player_stats(info, skaters, goalies)
        return dd_to_regular(skaters), dd_to_regular(goalies)

    def get_game_feeds(self):
        games_url = f'{self.base_stats_url}/api/v1/schedule?startDate={self.start_date}&endDate={self.end_date}'
        stats_resp = requests.get(games_url).json()
        feeds_by_date = defaultdict(set)
        for date_dict in stats_resp['dates']:
            LOGGER.info(f'Collecting stats for {date_dict["totalGames"]} games on {date_dict["date"]}')
            for game in date_dict['games']:
                g_date, g_feed = self.parse_date_and_feed(game)
                feeds_by_date[g_date].add(g_feed)
        return [f for feeds in feeds_by_date.values() for f in feeds]

    async def get_game_stats_raw(self, game_feeds):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for feed in game_feeds:
                tasks.append(self.parse_game_stats(game_feed=feed, session=session))
            return await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    def get_player_stats(game_dicts):
        parsed = {
            'skaters': {},
            'goalies': {}
        }
        LOGGER.info(f'Recorded {len(game_dicts)} games total.')
        for skaters, goalies in game_dicts:
            for skater, stats in skaters.items():
                if skater in parsed['skaters']:
                    for stat in stats:
                        parsed['skaters'][skater][stat] += stats[stat]
                else:
                    parsed['skaters'][skater] = stats
            for goalie, stats in goalies.items():
                if goalie in parsed['goalies']:
                    for stat in stats:
                        parsed['goalies'][goalie][stat] += stats[stat]
                else:
                    parsed['goalies'][goalie] = stats

                shots = parsed['goalies'][goalie]['shots']
                saves = parsed['goalies'][goalie]['saves']
                if shots > 0:
                    parsed['goalies'][goalie]['sv %'] = f'{round(saves/shots, 3):3.3f}'

        return parsed

    def write_stats(self, stats):
        current_dir = Path(__file__).parent.absolute()
        project_dir = current_dir.joinpath('..')
        output_dir = project_dir.joinpath('output')
        output_file = os.path.join(output_dir, f'{self.start_date}_to_{self.end_date}.json')

        LOGGER.info('Writing stats to: %s' % os.path.abspath(output_file))

        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=4)


if __name__ == '__main__':
    print(f"Started at {time.strftime('%X')}")

    args = docopt(__doc__)
    start, end = StatsScraper.get_start_and_end_dates(args)

    scraper = StatsScraper(start, end)

    game_feeds = scraper.get_game_feeds()
    game_dicts = asyncio.run(scraper.get_game_stats_raw(game_feeds))
    player_stats = scraper.get_player_stats(game_dicts)

    scraper.write_stats(player_stats)

    print(f"Ended at {time.strftime('%X')}")
