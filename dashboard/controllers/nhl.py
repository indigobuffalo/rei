import asyncio
from typing import Dict

from dashboard.nhl import StatsScraper


class NHLController:

    FILTERS_MAP = {
        'name': str,
        'limit': int,
    }

    def __init__(self, start, end):
        scraper = StatsScraper(start, end)
        game_feeds = scraper.get_game_feeds()
        stats_raw = asyncio.run(scraper.get_game_stats_raw(game_feeds))

        self.stats = scraper.get_player_stats(stats_raw)
        self.skater_stats = self.stats['skaters']
        self.goalie_stats = self.stats['goalies']

    def _validate_filters(self, filters: Dict):
        for f, f_val in filters.items():
            try:
                if self.FILTERS_MAP[f] != type(f_val):
                    raise ValueError(
                        f"Invalid type '{type(f_val)}' for filter '{f}'"
                    )
            except KeyError:
                raise KeyError(f"Invalid filter '{f}'")

    def filter_results(self, stats: Dict, filters: Dict = None):

        if not filters:
            return stats
        self._validate_filters(filters)
        name = filters.get('name')
        limit = filters.get('limit')
        if name:
            filtered = {k: v for k, v in stats.items() if name in k}
        else:
            filtered = stats
        return filtered[0:limit] if limit else filtered

    def get_stats(self, filters: Dict = None):
        unfiltered = {**self.skater_stats, **self.goalie_stats}
        return self.filter_results(unfiltered, filters)

    def get_skater_stats(self, filters: Dict = None):
        unfiltered = self.skater_stats
        return self.filter_results(unfiltered, filters)

    def get_goalie_stats(self, filters: Dict = None):
        unfiltered = self.goalie_stats
        return self.filter_results(unfiltered, filters)
