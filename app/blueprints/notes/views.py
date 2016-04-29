# -*- coding: utf-8 -*-
"""
Notes views
"""

import datetime

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for)
from flask_login import current_user
from flask.ext.security import login_required
from sqlalchemy import desc
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from app.blueprints.notes.email_tip import EmailTip
from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


def two_mins_ago():
    return datetime.datetime.utcnow() - datetime.timedelta(minutes=2)


@notes.context_processor
def notes_context():
    return {'undo_timeout': two_mins_ago}


def get_or_404(class_, **kwargs):
    try:
        return class_.query.filter_by(**kwargs).one()

    except NoResultFound:
        abort(404)

    except MultipleResultsFound:
        raise


@notes.route('/notes')
@login_required
def list():
    notes = Note.query.filter(Note.author == current_user)
    notes = notes.order_by(desc(Note.updated)).all()

    email_tip = EmailTip()
    email_tip.incr_times_seen()

    return render_template('notes/list.html', notes=notes)


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
    note = get_or_404(Note, id=id, author=current_user)

    try:
        note.revert()

    except note.VersionDoesNotExist:
        pass

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/edit', methods=['POST'])
@login_required
def edit(id):
    note = get_or_404(Note, id=id, author=current_user)

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
