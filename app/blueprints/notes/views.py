# -*- coding: utf-8 -*-
"""
Notes views
"""

import datetime

from flask import (
    Blueprint,
    after_this_request,
    redirect,
    render_template,
    request,
    url_for)
from sqlalchemy import desc

from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


@notes.route('/notes')
def list():
    all_notes = Note.query.order_by(desc(Note.updated)).all()
    two_mins_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=2)

    times_seen = int(request.cookies.get('seen_email_tip', 0))
    show_tip = times_seen < 2

    @after_this_request
    def set_cookie(response):
        times = str(times_seen)

        if show_tip:
            times = str(times_seen + 1)

        response.set_cookie('seen_email_tip', times)

        return response

    return render_template(
        'notes/list.html',
        notes=all_notes,
        inbox_email='your-inbox@civilservice.digital',
        show_tip=show_tip,
        undo_timeout=two_mins_ago)


@notes.route('/notes', methods=['POST'])
def add():
    content = request.form.get('content', '').strip()

    if content:
        Note.create(content)

    return redirect(url_for('.list'))


@notes.route('/notes/dismiss-email-tip')
def dismiss_tip():

    @after_this_request
    def set_cookie(response):
        response.set_cookie('seen_email_tip', '2')
        return response

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/undo', methods=['POST'])
def undo(id):
    note = Note.query.get(id)

    try:
        note.revert()

    except note.VersionDoesNotExist:
        pass

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/edit', methods=['POST'])
def edit(id):
    note = Note.query.get(id)

    note.update(request.form['content'])

    return redirect(url_for('.list'))
