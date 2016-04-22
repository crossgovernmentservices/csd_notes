from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def example_note():
    note = Note.create('Original content')
    return note


@pytest.fixture
def form_submit(client, example_note, logged_in):
    return client.post(url_for('notes.edit', id=example_note.id), data={
        'content': 'In ur notes, changin ur texts'})


@pytest.fixture
def follow_redirect(client, form_submit, logged_in):
    return client.get(form_submit.headers['Location'])


@pytest.fixture
def soup(follow_redirect):
    return BeautifulSoup(follow_redirect.get_data(as_text=True), 'html.parser')


class WhenUpdatingANote(object):

    def it_redirects_to_the_list_view(self, db_session, form_submit):
        assert form_submit.status_code == 302
        assert url_for('notes.list') in form_submit.headers['Location']

    def it_updates_the_list_view(self, db_session, soup):
        notes = soup.find_all(class_='note')
        content = str(notes[0].find(itemprop='text'))
        assert 'In ur notes, changin ur texts' in content
