from flask import Blueprint, request, jsonify
from flask.views import MethodView

from dashboard.presenters.rei import REIPresenter


class REIView(MethodView):
    def __init__(self):
        self.presenter = REIPresenter()

    def get(self):
        args = request.args.to_dict()

        filters = {}
        if 'stores' in args:
            filters['stores'] = args['stores'].split(',')
        return jsonify(self.presenter.get_garage_sales(filters))

    def post(self):
        pass

    def delete(self, user_id):
        pass

    def put(self, user_id):
        pass


rei_view = REIView.as_view('nhl_view')

bp = Blueprint('rei', __name__, url_prefix='/rei')
bp.add_url_rule(
    '',
    view_func=REIView.as_view('get'),
    methods=['GET']
)
