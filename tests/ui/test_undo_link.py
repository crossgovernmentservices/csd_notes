import contextlib
import datetime
from mock import patch

from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def updated_note(db_session):
    note = Note.create('Original text')
    note.update('Updated text')
    return note


@contextlib.contextmanager
def utcnow(module, value):
    with patch(module) as dt:
        dt.utcnow.return_value = value
        dt.side_effect = datetime.datetime
        yield


class WhenANoteHasBeenUpdated(object):

    def it_has_an_undo_link_until_the_user_clicks_away(
            self, live_server, updated_note, browser):

        browser.visit(url_for('notes.list', _external=True))

        undo_link = browser.find_by_css(
            '.notes-list .note:first-of-type .undo-link').first

        assert undo_link.visible

        browser.find_by_css('.add-note-form').first.click()

        assert not undo_link.visible

    def it_hides_the_undo_link_after_a_specified_period(
            self, db_session, live_server, updated_note, browser):

        now = datetime.datetime(2016, 4, 11, 13, 0, 0)
        two_mins_ago = now - datetime.timedelta(minutes=7)

        with utcnow('app.blueprints.notes.models.datetime.datetime', now):
            updated_note.updated = two_mins_ago
            db_session.add(updated_note)
            db_session.commit()

        with utcnow('app.blueprints.notes.views.datetime.datetime', now):
            browser.visit(url_for('notes.list', _external=True))

        note = browser.find_by_css(
            '.note[data-id="{}"]'.format(updated_note.id)).first

        assert not note.find_by_css('.undo-link')
