from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def updated_note(db_session):
    note = Note.create('Original text')
    note.update('Updated text')
    return note


class WhenANoteHasBeenUpdated(object):

    def it_has_an_undo_link_until_the_user_clicks_away(
            self, updated_note, selenium):

        selenium.get(url_for('notes.list', _external=True))

        undo_link = selenium.find_element_by_css_selector(
            '.notes-list .note:first-of-type .undo-link')

        assert undo_link.is_displayed()

        selenium.find_element_by_css_selector('.add-note-form').click()

        assert not undo_link.is_displayed()
