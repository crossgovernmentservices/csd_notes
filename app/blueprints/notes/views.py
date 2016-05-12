# -*- coding: utf-8 -*-
"""
Notes views
"""

from flask import (
    Blueprint,
    escape,
    jsonify,
    redirect,
    render_template,
    request,
    url_for)
from flask_login import current_user
from flask.ext.security import login_required
from sqlalchemy import desc

from app.blueprints.notes.email_tip import EmailTip
from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


@notes.route('/notes')
@login_required
def list():
    notes = Note.query.filter_by(author=current_user)
    notes = notes.order_by(desc(Note.updated)).all()

    email_tip = EmailTip()
    email_tip.incr_times_seen()

    return render_template('notes/list.html', notes=notes)


@notes.route('/notes', methods=['POST'])
@login_required
def add():
    content = request.form.get('content', '').strip()

    if content:
        Note.create(content=content, author=current_user)

    return redirect(url_for('.list'))


@notes.route('/notes/dismiss-email-tip')
def dismiss_tip():
    email_tip = EmailTip()
    email_tip.times_seen = 2

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/undo', methods=['POST'])
@login_required
def undo(id):
    note = Note.get_or_404(id=id, author=current_user)

    try:
        note.revert()

    except note.VersionDoesNotExist:
        pass

    return redirect(url_for('.list'))


@notes.route('/notes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    note = Note.get_or_404(id=id, author=current_user)

    if request.method == 'GET':
        return render_template('notes/edit.html', note=note)

    note.update(request.form['content'])
    return redirect(url_for('.list'))


@notes.route('/notes/search.json')
@login_required
def search_json():
    term = request.args.get('q')
    notes = Note.search(term).all()
    return jsonify({'results': [note.json for note in notes]})


@notes.route('/notes/search')
@login_required
def search():
    term = escape(request.args.get('q'))
    results = Note.search(term)
    ctx = {
        'notes': results.all(),
        'search_term': term,
        'result_count': results.count()}
    return render_template('notes/search.html', **ctx)
