from bs4 import BeautifulSoup
from flask import url_for
from markupsafe import Markup
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def some_notes(db_session):
    content = '*Test note {{}}*\n{}'.format(
        'All work and no play makes Jack a dull boy\n' * 10)
    return [Note.create(content.format(i)) for i in range(1, 4)]


@pytest.fixture
def response(client, some_notes):
    return client.get(url_for('notes.list'))


@pytest.fixture
def soup(response):
    return BeautifulSoup(response.get_data(as_text=True), 'html.parser')


@pytest.mark.use_fixtures('soup')
class TestWhenViewingNotesListPage(object):

    def test_it_lists_notes_in_reverse_chronological_order(self, soup):
        notes = soup.find_all(class_='note')
        assert len(notes) == 3

        def timestamp(note):
            return note.find(itemprop='dateModified')['data-timestamp']

        assert timestamp(notes[0]) >= timestamp(notes[1])
        assert timestamp(notes[1]) >= timestamp(notes[2])

    def test_it_renders_note_contents_as_markdown(self, soup):
        note = soup.find_all(class_='note')[0]
        assert len(note.find_all('em')) > 0

    def test_it_shows_only_the_first_250_characters_of_a_note(self, soup):
        notes = soup.find_all(class_='note')
        for note in notes:
            assert len(Markup(note.find(itemprop='text')).striptags()) <= 250
