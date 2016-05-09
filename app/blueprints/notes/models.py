# -*- coding: utf-8 -*-
"""
Notes models
"""

import datetime

from bs4 import BeautifulSoup

from app.extensions import db


def sanitize(content):
    soup = BeautifulSoup(content, 'html.parser')
    nodes = soup.recursiveChildGenerator()
    text_nodes = [e for e in nodes if isinstance(e, str)]
    return ''.join(text_nodes)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    is_email = db.Column(db.Boolean)
    history = db.relationship('NoteHistory', backref='note', cascade='delete')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='notes')

    class VersionDoesNotExist(Exception):

        def __init__(self, note, version):
            super(Note.VersionDoesNotExist, self).__init__(
                'Note version {} not found in history of note {}'.format(
                    version,
                    note.id))

    @classmethod
    def create(cls, content, author, is_email=False):
        note = Note(
            content=sanitize(content),
            author=author,
            is_email=is_email)
        note.created = datetime.datetime.utcnow()
        note.updated = note.created
        db.session.add(note)
        db.session.commit()
        return note

    def update(self, content):
        now = datetime.datetime.utcnow()
        version = NoteHistory(self, now)
        db.session.add(version)
        self.history.append(version)
        self.content = sanitize(content)
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
