# -*- coding: utf-8 -*-
"""
Report status of connected resources
"""

from flask import Blueprint, jsonify


healthcheck = Blueprint('healthcheck', __name__)


@healthcheck.route('/healthcheck.json')
def check_health():
    status = {
        'site': True}

    code = 200
    if not all(status.values()):
        code = 500

    return jsonify(status), code
