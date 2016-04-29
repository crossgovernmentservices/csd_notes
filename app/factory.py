# -*- coding: utf-8 -*-

import os

from flask import Flask, render_template


def create_app(config='config.py', **kwargs):
    """
    App factory function
    """

    app = Flask(__name__)
    app.config.from_pyfile(config)
    app.config.update(kwargs)

    register_blueprints(app)
    register_context_processors(app)
    register_error_handlers(app)
    register_extensions(app)
    register_filters(app)

    return app


def register_error_handlers(app):
    """
    Assign error page templates to all error status codes we care about
    """

    error_handlers = {
        '404.html': [404],
        '4xx.html': [401, 402, 405, 406, 407, 408, 409],
        '5xx.html': [500, 501, 502, 503, 504, 505]}

    def make_handler(code, template):
        template = os.path.join('errors', template)

        def handler(e):
            return render_template(template, code=code), code

        return handler

    for template, codes in error_handlers.items():
        for code in codes:
            app.register_error_handler(code, make_handler(code, template))


def register_blueprints(app):
    """
    Import and register blueprints
    """

    # XXX must come first as defines User and Role model classes
    from app.blueprints.base.views import base
    app.register_blueprint(base)

    from app.blueprints.healthcheck.views import healthcheck
    app.register_blueprint(healthcheck)

    from app.blueprints.notes.views import notes
    app.register_blueprint(notes)

    from app.blueprints.sso.views import sso
    app.register_blueprint(sso)


def register_context_processors(app):
    """
    Add template context variables and functions
    """

    def base_context_processor():
        return {
            'asset_path': '/static/govuk_template/assets/'
        }

    app.context_processor(base_context_processor)


def register_extensions(app):
    """
    Import and register flask extensions and initialize with app object
    """

    from app.assets import env
    env.init_app(app)

    from app.extensions import db
    db.init_app(app)
    # XXX avoids "RuntimeError: application not registered on db instance and
    # no application bound to current context" when accessing db outside of app
    # context
    db.app = app

    from flask.ext.migrate import Migrate
    from sqlalchemy.exc import ArgumentError
    migrate = Migrate()
    # XXX SQLite chokes on constraint changes without this
    with app.app_context():
        try:
            render_as_batch = db.engine.url.drivername == 'sqlite'

        # XXX this happens during a test
        except ArgumentError:
            render_as_batch = True

        migrate.init_app(app, db, render_as_batch=bool(render_as_batch))

    from flaskext.markdown import Markdown
    Markdown(app, extensions=app.config.get('MARKDOWN_EXTENSIONS', []))

    from flask.ext.humanize import Humanize
    Humanize(app)

    from app.extensions import oidc
    oidc.init_app(app)

    from flask.ext.security import Security
    from app.extensions import user_datastore
    from app.blueprints.base.models import Role, User
    user_datastore.role_model = Role
    user_datastore.user_model = User
    Security(app, user_datastore)


def register_filters(app):
    """
    Import and register Jinja filters
    """

    from lib.html_truncation import truncate_html
    from markupsafe import Markup

    def truncate(*args, **kwargs):
        return Markup(truncate_html(*args, **kwargs))

    app.jinja_env.filters['truncate_html'] = truncate
