import time

from flask import Blueprint, request, g
from flask.views import MethodView

from dashboard.controllers.nhl import NHLController


class NHLView(MethodView):
    def __init__(self):
        self.controller = NHLController(g.start_date, g.end_date)

    def get(self):
        view = request.endpoint.split('.')[1]
        if view == 'skaters':
            return self.controller.get_skater_stats()
        if view == 'goalies':
            return self.controller.get_goalie_stats()
        if view == 'scores':
            return 'Did you mean to hit the "skater" or "goalies" endpoint?'

    def post(self):
        pass

    def delete(self, user_id):
        pass

    def put(self, user_id):
        pass


nhl_view = NHLView.as_view('nhl_view')

bp = Blueprint('nhl', __name__, url_prefix='/nhl')
bp.add_url_rule(
    '',
    view_func=NHLView.as_view('scores'),
    methods=['GET']
)
bp.add_url_rule(
    '/skaters',
    view_func=NHLView.as_view('skaters'),
    methods=['GET']
)
bp.add_url_rule(
    '/goalies',
    view_func=NHLView.as_view('goalies'),
    methods=['GET']
)


@bp.before_request
def set_start_and_end_dates():
    today = time.strftime('%Y-%m-%d')
    args = request.args.to_dict()
    start = args.get('start') or today
    end = args.get('end') or today

    g.start_date = start
    g.end_date = end
