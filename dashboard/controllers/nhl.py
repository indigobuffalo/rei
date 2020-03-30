import asyncio

from dashboard.nhl import StatsScraper


class NHLController:
    def __init__(self, start, end):
        scraper = StatsScraper(start, end)
        game_feeds = scraper.get_game_feeds()
        stats_raw = asyncio.run(scraper.get_game_stats_raw(game_feeds))
        self.stats = scraper.get_game_stats_parsed(stats_raw)

    def get_stats(self):
        return self.stats

    def get_skater_stats(self):
        return self.stats['skaters']

    def get_goalie_stats(self):
        return self.stats['goalies']
