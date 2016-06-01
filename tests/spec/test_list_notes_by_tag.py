from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def notes(db_session, test_user):

    notes = []
    notes += [('note 1', ['foo'])]
    notes += [('note 2', ['bar'])] * 2
    notes += [('note 3', ['quux'])] * 25

    def make_note(data):
        content, tags = data

        note = Note.create(content=content, author=test_user)

        for tag in tags:
            note.add_tag(tag)

        return note

    return list(map(make_note, notes))


@pytest.fixture
def by_tag(client):

    def filter_notes(tag):
        response = client.get(url_for('notes.by_tag', tag=tag))
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        return soup

    return filter_notes


@pytest.mark.usefixtures('logged_in')
class WhenViewingAListOfNotesFilteredByTag(object):

    def it_shows_no_notes_if_there_are_none(self, by_tag):
        soup = by_tag('flibble')
        assert len(soup.find_all(class_='note')) == 0

        assert '0 notes found' in soup.text

    @pytest.mark.parametrize('tag,expected', [
        ('foo', 1),
        ('bar', 2),
        ('quux', 25)])
    def it_shows_a_list_of_matching_notes(self, notes, by_tag, tag, expected):
        soup = by_tag(tag)
        assert len(soup.find_all(class_='note')) == expected
