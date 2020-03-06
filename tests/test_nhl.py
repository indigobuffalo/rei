import os

from dashboard.nhl import parse_date_and_feed, STATS_URL


def test_parse_date_and_feed():
    game_feed = {
        'gameDate': '2020-03-07T02:00:00Z',
        'link': '/api/v1/game/2019021046/feed/live',
        'venue': {
            'id': 5075,
            'link': '/api/v1/venues/5075',
            'name': 'Scotiabank Saddledome'
        }
}
    date, feed = parse_date_and_feed(game_feed)
    assert date == '2020-03-06'
    assert feed == f'{STATS_URL}/api/v1/game/2019021046/feed/live'

