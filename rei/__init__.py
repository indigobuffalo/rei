from pathlib import Path

import yaml
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from rei.views.sales import bp as sales_bp

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    cfg_file = Path(__file__).parents[1].joinpath('config.yaml')
    with open(cfg_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    app.config.from_mapping(cfg)

    app.register_blueprint(sales_bp)

    @app.route('/')
    def route():
        return jsonify([bp.url_prefix for bp in app.blueprints.values()])

    db.init_app(app)

    return app
