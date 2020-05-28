from pathlib import Path

import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dashboard.views.nhl import bp as nhl_bp
from dashboard.views.rei import bp as rei_bp

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    cfg_file = Path(__file__).parents[1].joinpath('config.yaml')
    with open(cfg_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.SafeLoader)
    app.config.from_mapping(cfg)

    @app.route('/')
    def route():
        return 'Hello, welcome home.'

    app.register_blueprint(nhl_bp)
    app.register_blueprint(rei_bp)

    db.init_app(app)

    return app
