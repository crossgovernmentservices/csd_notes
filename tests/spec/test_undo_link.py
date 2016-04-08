from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def updated_note():
    note = Note.create('Original content')
    note.update('Updated content')
    return note


@pytest.fixture
def undo_submit(client, updated_note):
    return client.post(url_for('notes.undo', id=updated_note.id))


@pytest.fixture
def follow_redirect(client, undo_submit):
    return client.get(undo_submit.headers['Location'])


@pytest.fixture
def soup(follow_redirect):
    return BeautifulSoup(follow_redirect.get_data(as_text=True), 'html.parser')


class WhenUndoingANoteUpdate(object):

    def it_redirects_to_the_list_view(self, db_session, undo_submit):
        assert undo_submit.status_code == 302
        assert url_for('notes.list') in undo_submit.headers['Location']

    def it_shows_previous_version_of_note(self, db_session, soup):
        notes = soup.find_all(class_='note')
        content = str(notes[0].find(itemprop='text'))
        assert 'Original content' in content
