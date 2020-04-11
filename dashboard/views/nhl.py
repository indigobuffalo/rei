import time

from flask import Blueprint, request, g
from flask.views import MethodView

from dashboard.presenters.nhl import NHLPresenter


class NHLView(MethodView):
    def __init__(self):
        self.presenter = NHLPresenter(g.start_date, g.end_date)

    def get(self):
        return self.presenter.get_stats()

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
    view_func=NHLView.as_view('all'),
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
