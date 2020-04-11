import asyncio
from datetime import datetime
from typing import Dict

from dashboard.orms.nhl import StatsScraper


class NHLPresenter:

    def __init__(self, start: str, end: str):
        scraper = StatsScraper(start, end)
        self.start = datetime.strptime(start, '%Y-%m-%d')
        self.end = datetime.strptime(end, '%Y-%m-%d')
        self.days = (self.end - self.start).days + 1

        game_feeds = scraper.get_game_feeds()
        stats_raw = asyncio.run(scraper.get_games_stats_raw(game_feeds))
        self.stats = scraper.get_player_stats(stats_raw)

    def _present(self) -> Dict:
        presented = {
            'metadata': {
                'dates': {
                    'days': self.days,
                    'start': datetime.strftime(self.start, '%Y-%m-%d'),
                    'end': datetime.strftime(self.end, '%Y-%m-%d')
                },
                'games': self.stats['games']
            },
            'skaters': {},
            'goalies': {}
        }
        for skater, stats in self.stats['skaters'].items():
            presented['skaters'][skater] = stats.json_normalized()
        for goalie, stats in self.stats['goalies'].items():
            presented['goalies'][goalie] = stats.json_normalized()
        return presented

    def get_stats(self):
        return self._present()
