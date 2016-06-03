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
from flask_security import login_required
from sqlalchemy import desc, func, or_

from app.blueprints.notes.email_tip import EmailTip
from app.blueprints.notes.models import Note, Tag


notes = Blueprint('notes', __name__)


@notes.route('/notes')
@login_required
def list():
    notes = Note.query.filter_by(author=current_user)
    notes = notes.order_by(desc(Note.updated)).all()

    email_tip = EmailTip()
    email_tip.incr_times_seen()

    return render_template('notes/list.html', notes=notes)


def submitted_tags():
    tag_data = {}
    for key, value in sorted(request.form.items()):
        if key.startswith('tag-'):
            index = int(''.join(x for x in key if x.isdigit()))
            _, _, key = key.rpartition('-')
            tag_data.setdefault(index, {})[key] = value

    return tag_data.values()


@notes.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    tags = Tag.query.filter(or_(
        Tag.author == current_user,
        Tag.author == None)).order_by(  # noqa
            func.lower(Tag.name))

    if request.method == 'POST':

        for data in submitted_tags():
            tag = Tag.query.get(data['id'])
            tag.update(**data)

        return redirect(url_for('.tags'))

    context = {
        'user_tags': tags.filter(Tag.namespace == None).all(),  # noqa
        'competency_tags': tags.filter(Tag.namespace == 'Competency').all(),
        'objective_tags': tags.filter(Tag.namespace == 'Objective').all(),
        'system_tags': tags.filter(Tag.namespace == 'System').all()
    }

    return render_template('notes/tags.html', **context)


@notes.route('/notes/tag/<tag>')
@login_required
def by_tag(tag):

    notes = Note.query.filter(Note.tags.any(name=tag)).order_by(
        desc(Note.updated)).all()

    return render_template('notes/by_tag.html', tag=tag, notes=notes)


@notes.route('/notes', methods=['POST'])
@login_required
def add():
    content = request.form.get('content', '').strip()
    tags = request.form.get('tags', '').split(',')

    if content:
        note = Note.create(content=content, author=current_user)

        for tag in tags:
            note.add_tag(tag.strip())

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

    existing_tags = set([tag.name for tag in note.tags])

    submitted_tags = set(
        [tag.strip() for tag in request.form.get('tags', '').split(',')])

    for tag in (submitted_tags - existing_tags):
        note.add_tag(tag)

    for tag in (existing_tags - submitted_tags):
        note.remove_tag(tag)

    return redirect(url_for('.list'))


@notes.route('/notes/search.json')
@login_required
def search_json():
    term = request.args.get('q')
    notes = Note.search(term, current_user).all()
    return jsonify({'results': [note.json for note in notes]})


@notes.route('/notes/search')
@login_required
def search():
    term = escape(request.args.get('q'))
    results = Note.search(term, current_user)
    ctx = {
        'notes': results.all(),
        'search_term': term,
        'result_count': results.count()}
    return render_template('notes/search.html', **ctx)
