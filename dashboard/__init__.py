from flask import Flask

from dashboard.views.nhl import bp as nhl_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/')
    def route():
        return 'Hello, welcome home.'

    app.register_blueprint(nhl_bp)

    return app
