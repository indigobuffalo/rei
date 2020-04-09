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
from typing import Dict, Tuple, List

import aiohttp
import asyncio
import requests

import pytz
from pytz import timezone
from docopt import docopt

from dashboard.log_helper import setup_stream_logger
from dashboard.models.goalie import Goalie
from dashboard.models.skater import Skater

LOGGER = setup_stream_logger()


def dd_to_regular(d):
    """Converts a defaultdict of defaultdicts to a dict of dicts"""
    if isinstance(d, defaultdict):
        d = {k: dd_to_regular(v) for k, v in d.items()}
    return d


def get_name_last_first(name: str):
    first, last = name.split(" ", 1)
    return f'{last}, {first}'


class StatsScraper:

    def __init__(self, start_date, end_date):
        self.base_stats_url = 'https://statsapi.web.nhl.com'

        self.start_date = start_date
        self.end_date = end_date
        self.game_feeds = None
        self.game_stats = None

    @staticmethod
    def is_skater(player_info):
        return player_info['position']['type'] in {'Forward', 'Defenseman'}

    @staticmethod
    def is_goalie(player_info):
        return player_info['position']['type'] == 'Goalie'

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

    def parse_date_and_feed(self, game: Dict) -> Tuple[str, str]:
        """"Parse game feed url from a game dictionary.

        The game feed resource contains stats for the game.
        """
        datetime_utc_naive = datetime.strptime(game['gameDate'], '%Y-%m-%dT%H:%M:%SZ')
        datetime_utc = pytz.utc.localize(datetime_utc_naive)
        datetime_pacific = datetime_utc.astimezone(timezone('US/Pacific'))
        game_date = datetime.strftime(datetime_pacific, '%Y-%m-%d')
        return game_date, self.base_stats_url + game['link']

    @staticmethod
    def instantiate_goalie(game_date: datetime, name: str, team: str, stats: Dict) -> Goalie:
        decision = stats['decision']
        loss = 1 if decision.upper() == 'L' else 0
        win = 1 if decision.upper() == 'W' else 0
        return Goalie(
            game_dates=[game_date],
            losses=loss,
            name=name,
            saves=stats['saves'],
            saves_ev=stats['evenSaves'],
            saves_pp=stats['shortHandedSaves'],
            saves_sh=stats['powerPlaySaves'],
            shots=stats['shots'],
            shots_ev=stats['evenShotsAgainst'],
            shots_pp=stats['shortHandedShotsAgainst'],
            shots_sh=stats['powerPlayShotsAgainst'],
            team=team,
            wins=win
        )

    @staticmethod
    def instantiate_skater(game_date: datetime, name: str, team: str, position: str, stats: Dict) -> Skater:
        return Skater(
            assists=stats['assists'],
            assists_pp=stats['powerPlayAssists'],
            assists_sh=stats['shortHandedAssists'],
            blocks=stats['blocked'],
            faceoff_pct=stats.get('faceOffPct'),
            faceoffs=stats['faceoffTaken'],
            faceoffs_won=stats['faceOffWins'],
            game_dates=[game_date],
            giveaways=stats['giveaways'],
            goals=stats['goals'],
            goals_pp=stats['powerPlayGoals'],
            goals_sh=stats['shortHandedGoals'],
            hits=stats['hits'],
            name=name,
            pim=stats['penaltyMinutes'],
            plus_minus=stats['plusMinus'],
            position=position,
            shots=stats['shots'],
            takeaways=stats['takeaways'],
            team=team,
            toi=stats['timeOnIce'],
            toi_ev=stats['evenTimeOnIce'],
            toi_pp=stats['powerPlayTimeOnIce'],
            toi_sh=stats['shortHandedTimeOnIce']
        )

    def parse_team_stats(self, team: str, game_date: datetime, players: Dict) -> Dict[str, Dict]:
        team_stats = {
            'skaters': {},
            'goalies': {}
        }
        for player in players.values():
            name = get_name_last_first(player['person']['fullName'])
            position = player['position']['code']
            if self.is_skater(player):
                stats = player['stats']['skaterStats']
                skater = self.instantiate_skater(
                    game_date=game_date,
                    name=name,
                    team=team,
                    position=position,
                    stats=stats
                )
                team_stats['skaters'][name] = skater
            elif self.is_goalie(player):
                stats = player['stats']['goalieStats']
                goalie = self.instantiate_goalie(
                    game_date=game_date,
                    name=name,
                    team=team,
                    stats=stats
                )
                team_stats['goalies'][name] = goalie
        return team_stats

    async def parse_game_stats(self, game_feed: str, session: aiohttp.ClientSession) -> Dict[str, Dict]:
        game_stats = {}
        resp = await session.get(game_feed)
        resp_json = await resp.json()

        box = resp_json['liveData']['boxscore']['teams']
        home_team = box['home']['team']['name']
        home_players = box['home']['players']
        away_team = box['away']['team']['name']
        away_players = box['away']['players']
        game_date_str = resp_json['gameData']['datetime']['dateTime'].split('T')[0]
        game_date = datetime.strptime(game_date_str, '%Y-%m-%d')

        away_stats = self.parse_team_stats(home_team, game_date, home_players)
        home_stats = self.parse_team_stats(away_team, game_date, away_players)

        game_stats['skaters'] = {**home_stats['skaters'], **away_stats['skaters']}
        game_stats['goalies'] = {**home_stats['goalies'], **away_stats['goalies']}

        return game_stats

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

    async def get_games_stats_raw(self, game_feeds):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for feed in game_feeds:
                tasks.append(self.parse_game_stats(game_feed=feed, session=session))
            return await asyncio.gather(*tasks)

    @staticmethod
    def get_player_stats(games_dicts: List[Dict]):
        cumulative = {
            'skaters': {},
            'goalies': {}
        }
        LOGGER.info(f'Recorded {len(games_dicts)} games total.')

        for game_dict in games_dicts:
            for name, model in game_dict['skaters'].items():
                if name in cumulative['skaters']:
                    # TODO: append to existing
                    pass
                else:
                    cumulative['skaters'][name] = model
            for name, model in game_dict['goalies'].items():
                if name in cumulative['goalies']:
                    cumulative['goalies'][name] += model
                else:
                    cumulative['goalies'][name] = model
        return cumulative

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
    games_feeds = scraper.get_game_feeds()
    games_stats = asyncio.run(scraper.get_games_stats_raw(games_feeds))
    players_stats = scraper.get_player_stats(games_stats)
    scraper.write_stats(players_stats)
    print(f"Ended at {time.strftime('%X')}")
