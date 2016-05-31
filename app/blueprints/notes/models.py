# -*- coding: utf-8 -*-
"""
Notes models
"""

import datetime

from bs4 import BeautifulSoup
from flask import current_app, url_for
from flask_sqlalchemy import BaseQuery
from sqlalchemy_searchable import SearchQueryMixin, make_searchable
from sqlalchemy_utils.types import TSVectorType

from app.extensions import db
from lib.model_utils import GetOr404Mixin, GetOrCreateMixin


make_searchable()


class NoteQuery(BaseQuery, SearchQueryMixin):
    pass


def sanitize(content):
    soup = BeautifulSoup(content, 'html.parser')
    nodes = soup.recursiveChildGenerator()
    text_nodes = [e for e in nodes if isinstance(e, str)]
    return ''.join(text_nodes)


tags = db.Table(
    'note_tag',
    db.Column('tag.id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('note.id', db.Integer, db.ForeignKey('note.id')))


class Note(db.Model, GetOr404Mixin, GetOrCreateMixin):
    query_class = NoteQuery

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    is_email = db.Column(db.Boolean)
    history = db.relationship('NoteHistory', backref='note', cascade='delete')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='notes')
    search_vector = db.Column(TSVectorType('content'))
    tags = db.relationship('Tag', backref='notes', secondary=tags)

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

    def add_tag(self, tag_name):
        if tag_name and not self.has_tag(tag_name):
            self.tags.append(Tag(name=sanitize(tag_name), author=self.author))
            db.session.add(self)
            db.session.commit()

    def has_tag(self, tag_name):
        return Note.query.join(tags).filter(
            Note.id == self.id,
            Tag.author == self.author,
            Tag.name == tag_name).count() > 0

    def remove_tag(self, tag_name):
        if self.has_tag(tag_name):
            tag = [tag for tag in self.tags if tag.name == tag_name]
            self.tags.remove(tag[0])
            db.session.add(self)
            db.session.commit()

    @classmethod
    def search(cls, term, user):
        return Note.query.filter(Note.author == user).search(
            term, sort=True)

    @property
    def rendered(self):
        markdown = current_app.jinja_env.filters['markdown']
        return markdown(self.content)

    @property
    def truncated(self):
        truncate = current_app.jinja_env.filters['truncate_html']
        return truncate(self.rendered, 250, end=" \u2026")

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
            'is_email': self.is_email,
            'tags': [{
                'name': tag.name,
                'url': tag.url} for tag in self.tags]
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


class Tag(db.Model, GetOr404Mixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    namespace = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref='tags')

    @property
    def url(self):
        return url_for('notes.by_tag', tag=self.name)

    @property
    def usage_count(self):
        return len(self.notes)
