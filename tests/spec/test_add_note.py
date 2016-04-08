from bs4 import BeautifulSoup
from flask import url_for
import pytest


@pytest.fixture
def form_submit(client):
    return client.post(url_for('notes.add'), data={
        'content': 'A *lovely* new note'})


@pytest.fixture
def follow_redirect(client, form_submit):
    return client.get(form_submit.headers['Location'])


@pytest.fixture
def soup(follow_redirect):
    return BeautifulSoup(follow_redirect.get_data(as_text=True), 'html.parser')


class WhenAddingANewNote(object):

    def it_redirects_to_the_list_view(self, db_session, form_submit):
        assert form_submit.status_code == 302
        assert url_for('notes.list') in form_submit.headers['Location']

    def it_updates_the_list_view(self, db_session, soup):
        notes = soup.find_all(class_='note')
        assert len(notes) > 0

        content = str(notes[0].find(itemprop='text'))
        assert 'A <em>lovely</em> new note' in content

        undo_link = notes[0].find(class_='undo-link')
        assert undo_link is None
