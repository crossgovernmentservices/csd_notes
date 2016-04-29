# -*- coding: utf-8 -*-
"""
Notes views
"""

import datetime

from flask import (
    Blueprint,
    after_this_request,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    url_for)
from flask_login import current_user
from flask.ext.security import login_required
from sqlalchemy import desc

from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


def two_mins_ago():
    return datetime.datetime.utcnow() - datetime.timedelta(minutes=2)


class EmailTip(object):

    def __init__(self):
        current_app.logger.debug('EmailTip constructed')
        self._times_seen = None
        self.set_template_context()

    @property
    def times_seen(self):
        if self._times_seen is None:
            self._times_seen = int(request.cookies.get('seen_email_tip', 0))
            current_app.logger.debug(
                'reading cookie: {}'.format(self._times_seen))

        return self._times_seen

    @times_seen.setter
    def times_seen(self, value):
        current_app.logger.debug('set times_seen to {}'.format(value))
        self._times_seen = value
        after_this_request(self.set_cookie)

    @property
    def visible(self):
        current_app.logger.debug('visible {}'.format(self.times_seen < 2))
        return self.times_seen < 2

    def incr_times_seen(self):
        if self.visible:
            current_app.logger.debug('incr_times_seen')
            self.times_seen += 1

    def set_cookie(self, response):
        current_app.logger.debug('set_cookie: {}'.format(self.times_seen))
        response.set_cookie('seen_email_tip', str(self.times_seen))
        return response

    def set_template_context(self):
        current_app.jinja_env.globals['email_tip_visible'] = self.visible
        current_app.logger.debug(
            'updated template global email_tip_visible={}'.format(
                self.visible))


@notes.context_processor
def notes_context():
    return {'undo_timeout': two_mins_ago}


@notes.route('/notes')
@login_required
def list():
    all_notes = Note.query.order_by(desc(Note.updated)).all()

    email_tip = EmailTip()
    email_tip.incr_times_seen()

    return render_template('notes/list.html', notes=all_notes)


@notes.route('/notes', methods=['POST'])
@login_required
def add():
    content = request.form.get('content', '').strip()

    if content:
        Note.create(content, current_user)

    return redirect(url_for('.list'))


@notes.route('/notes/dismiss-email-tip')
def dismiss_tip():

    email_tip = EmailTip()
    email_tip.times_seen = 2

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/undo', methods=['POST'])
@login_required
def undo(id):
    note = Note.query.get(id)

    try:
        note.revert()

    except note.VersionDoesNotExist:
        pass

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/edit', methods=['POST'])
@login_required
def edit(id):
    note = Note.query.get(id)

    note.update(request.form['content'])

    return redirect(url_for('.list'))


@notes.route('/notes/search.json')
@login_required
def search_json():
    term = request.args.get('q')
    return jsonify({'results': [note.json for note in Note.search(term)]})


@notes.route('/notes/search')
@login_required
def search():
    term = request.args.get('q')
    return render_template('notes/list.html', notes=Note.search(term))
