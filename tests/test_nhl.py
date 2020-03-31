import pytest

from dashboard.nhl import StatsScraper


@pytest.fixture
def scraper():
    return StatsScraper(start_date='2020-03-01', end_date='2020-03-31')


class TestStatScraper:

    def test_parse_date_and_feed(self, scraper):
        game_feed = {
            'gameDate': '2020-03-07T02:00:00Z',
            'link': '/api/v1/game/2019021046/feed/live',
            'venue': {
                'id': 5075,
                'link': '/api/v1/venues/5075',
                'name': 'Scotiabank Saddledome'
            }
        }
        date, feed = scraper.parse_date_and_feed(game_feed)
        assert date == '2020-03-06'
        assert feed == f'{scraper.base_stats_url}/api/v1/game/2019021046/feed/live'
