# -*- coding: utf-8 -*-
"""
Notes views
"""

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import desc

from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


@notes.route('/notes')
def list():
    all_notes = Note.query.order_by(desc(Note.updated)).all()
    return render_template('notes/list.html', notes=all_notes)


@notes.route('/notes', methods=['POST'])
def add():
    content = request.form.get('content', '').strip()

    if content:
        Note.create(content)

    return redirect(url_for('.list'))
