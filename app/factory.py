# -*- coding: utf-8 -*-

import os

from flask import Flask, render_template


def create_app(config=None):
    """
    App factory function
    """

    app = Flask(__name__)
    app.config.from_object(config)

    register_error_handlers(app)
    register_blueprints(app)
    register_context_processors(app)
    register_extensions(app)

    return app


def register_error_handlers(app):
    """
    Assign error page templates to all error status codes we care about
    """

    error_handlers = {
        '404.jinja': [404],
        '4xx.jinja': [401, 402, 405, 406, 407, 408, 409],
        '5xx.jinja': [500, 501, 502, 503, 504, 505]}

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

    from app.blueprints.base.views import base
    app.register_blueprint(base)


def register_context_processors(app):
    """
    Add template context variables and functions
    """

    def base_context_processor():
        return {}

    app.context_processor(base_context_processor)


def register_extensions(app):
    """
    Import and register flask extensions and initialize with app object
    """
    pass
