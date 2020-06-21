from flask import Blueprint, request, jsonify
from flask.views import MethodView

from rei.presenters.sales import SalesPresenter


class SalesView(MethodView):
    def __init__(self):
        self.presenter = SalesPresenter()

    def get(self):
        view = request.endpoint.split('.')[-1]
        if view == 'root':
            return jsonify(['/garage'])
        if view == 'garage':
            return jsonify(self.presenter.get_garage_sales())

    def post(self):
        pass

    def delete(self, user_id):
        pass

    def put(self, user_id):
        pass


rei_view = SalesView.as_view('rei_view')

bp = Blueprint('sales', __name__, url_prefix='/sales')
bp.add_url_rule(
    '',
    view_func=SalesView.as_view('root'),
    methods=['GET']
)
bp.add_url_rule(
    'garage',
    view_func=SalesView.as_view('garage'),
    methods=['GET']
)
