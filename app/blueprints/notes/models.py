# -*- coding: utf-8 -*-
"""
Notes models
"""

import datetime
from flask import current_app, url_for

from bs4 import BeautifulSoup

from app.extensions import db


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    is_email = db.Column(db.Boolean)
    history = db.relationship('NoteHistory', backref='note', cascade='delete')

    class VersionDoesNotExist(Exception):

        def __init__(self, note, version):
            super(Note.VersionDoesNotExist, self).__init__(
                'Note version {} not found in history of note {}'.format(
                    version,
                    note.id))

    def set_content(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        nodes = soup.recursiveChildGenerator()
        text_nodes = [e for e in nodes if isinstance(e, str)]
        self.content = ''.join(text_nodes)

    @classmethod
    def create(cls, content, is_email=False):
        note = Note()
        note.set_content(content)
        note.created = datetime.datetime.utcnow()
        note.updated = note.created
        note.is_email = is_email
        db.session.add(note)
        db.session.commit()
        return note

    def update(self, content):
        now = datetime.datetime.utcnow()
        version = NoteHistory(self, now)
        db.session.add(version)
        self.history.append(version)
        self.set_content(content)
        self.updated = now
        db.session.add(self)
        db.session.commit()

    def revert(self, version=None):
        if version is None:
            version = len(self.history) - 1

        versions = {rev.version: rev for rev in self.history}

        if version not in versions:
            raise Note.VersionDoesNotExist(self, version)

        self.update(versions[version].content)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def truncated(self):
        markdown = current_app.jinja_env.filters['markdown']
        truncate = current_app.jinja_env.filters['truncate_html']
        return truncate(markdown(self.content), 250, end=" \u2026")

    @property
    def edit_url(self):
        return url_for('notes.edit', id=self.id)

    @property
    def just_updated(self):
        undo_timeout = (
            datetime.datetime.utcnow() - datetime.timedelta(minutes=2))
        return bool(self.history and self.updated > undo_timeout)

    @property
    def undo_url(self):
        return url_for('notes.undo', id=self.id)

    @property
    def timestamp(self):
        return self.updated.strftime('%Y%m%d%H%M%S.%f')

    @property
    def friendly_updated(self):
        humanize = current_app.jinja_env.filters['humanize']
        return humanize(self.updated)

    def json(self):
        return {
            'id': self.id,
            'truncated': self.truncated,
            'edit_url': self.edit_url,
            'content': self.content,
            'just_updated': self.just_updated,
            'undo_url': self.undo_url,
            'timestamp': self.timestamp,
            'friendly_updated': self.friendly_updated,
            'is_email': self.is_email
        }


class NoteHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    version = db.Column(db.Integer)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime)

    def __init__(self, note, now):
        self.note = note
        self.created = now
        self.content = note.content
        self.version = 0
        versions = [rev.version for rev in note.history]
        if versions:
            self.version = max(0, *versions) + 1
