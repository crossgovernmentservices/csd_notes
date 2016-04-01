# -*- coding: utf-8 -*-
"""
Notes views
"""

from flask import Blueprint, render_template
from sqlalchemy import desc

from app.blueprints.notes.models import Note


notes = Blueprint('notes', __name__)


@notes.route('/notes')
def list():
    all_notes = Note.query.order_by(desc(Note.updated)).all()
    return render_template('notes/list.html', notes=all_notes)
