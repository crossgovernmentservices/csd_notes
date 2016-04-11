import contextlib
import datetime
from mock import patch

from flask import url_for
import pytest
from selenium.common.exceptions import NoSuchElementException

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
            self, updated_note, selenium):

        selenium.get(url_for('notes.list', _external=True))

        undo_link = selenium.find_element_by_css_selector(
            '.notes-list .note:first-of-type .undo-link')

        assert undo_link.is_displayed()

        selenium.find_element_by_css_selector('.add-note-form').click()

        assert not undo_link.is_displayed()

    def it_hides_the_undo_link_after_a_specified_period(
            self, db_session, updated_note, selenium):

        now = datetime.datetime(2016, 4, 11, 13, 0, 0)
        two_mins_ago = now - datetime.timedelta(minutes=7)

        with utcnow('app.blueprints.notes.models.datetime.datetime', now):
            updated_note.updated = two_mins_ago
            db_session.add(updated_note)
            db_session.commit()

        with utcnow('app.blueprints.notes.views.datetime.datetime', now):
            selenium.get(url_for('notes.list', _external=True))

        note = selenium.find_element_by_css_selector(
            '.note[data-id="{}"]'.format(updated_note.id))

        with pytest.raises(NoSuchElementException):
            note.find_element_by_class_name('undo-link')
