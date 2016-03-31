# -*- coding: utf-8 -*-
"""
Notes views
"""

from flask import Blueprint, render_template

from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


@notes.route('/notes')
def list():
    all_notes = Note.query.all()
    return render_template('notes/list.html', notes=all_notes)
