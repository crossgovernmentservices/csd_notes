from http.cookies import SimpleCookie

from bs4 import BeautifulSoup
from flask import url_for
from markupsafe import Markup
import pytest

from app.blueprints.base.models import User
from app.blueprints.notes.models import Note


@pytest.fixture
def notes(db_session, test_user):
    other_user = User(email='test2@example.com', full_name='Testy McTestface')
    db_session.add(other_user)
    db_session.commit()
    content = 'This is not your note'
    return (
        [Note.create(content='*foo*', author=test_user) for i in range(3)] +
        [Note.create(content=content, author=other_user) for i in range(3)])


@pytest.fixture
def list_response(client):
    return client.get(url_for('notes.list'))


def cookies(response):
    cookies = SimpleCookie()
    for header in response.headers.getlist('Set-Cookie'):
        cookies.load(header)
    return cookies


@pytest.fixture
def list_cookies(list_response):
    return cookies(list_response)


@pytest.fixture
def list_html(list_response):
    return list_response.get_data(as_text=True)


@pytest.fixture
def list_soup(list_html):
    return BeautifulSoup(list_html, 'html.parser')


@pytest.fixture
def seen_twice(client, logged_in):
    client.set_cookie('localhost', 'seen_email_tip', '2')
    response = client.get(url_for('notes.list'))
    return response


@pytest.fixture
def seen_twice_soup(seen_twice):
    return BeautifulSoup(seen_twice.get_data(as_text=True), 'html.parser')


@pytest.fixture
def dismiss_tip_cookies(client):
    return cookies(client.get(url_for('notes.dismiss_tip')))


@pytest.mark.usefixtures('logged_in', 'notes')
class WhenViewingNotesListPage(object):

    def it_shows_a_list_of_notes(self, list_soup):
        assert list_soup.find(class_='notes-list')
        assert len(list_soup.find_all(class_='note')) > 1

    def it_only_shows_notes_by_the_current_user(self, list_html, list_soup):
        assert len(list_soup.find_all(class_='note')) == 3
        assert 'This is not your note' not in list_html

    def it_lists_notes_in_reverse_chronological_order(self, list_soup):
        notes = list_soup.find_all(class_='note')
        assert len(notes) >= 3

        def timestamp(note):
            return note.find(itemprop='dateModified')['data-timestamp']

        assert timestamp(notes[0]) >= timestamp(notes[1])
        assert timestamp(notes[1]) >= timestamp(notes[2])

    def it_renders_note_contents_as_markdown(self, list_soup):
        note = list_soup.find_all(class_='note')[0]
        assert len(note.find_all('em')) > 0

    def it_shows_only_first_250_chars_of_a_note(self, list_soup):
        notes = list_soup.find_all(class_='note')
        for note in notes:
            assert len(Markup(note.find(itemprop='text')).striptags()) <= 250

    def it_shows_the_email_tip(self, list_soup):
        tip = list_soup.find(class_='message-box')
        assert tip.find('a')['href'].startswith('mailto:')

    def it_sets_cookie_if_tip_not_seen_twice_already(self, list_cookies):
        assert 'seen_email_tip' in list_cookies
        assert int(list_cookies['seen_email_tip'].value) == 1

    def it_hides_the_email_tip_if_seen_twice_already(self, seen_twice_soup):
        tip = seen_twice_soup.find(class_='message-box')
        assert tip is None


class WhenDismissingTheEmailTip(object):

    def it_sets_a_cookie(self, dismiss_tip_cookies):
        assert 'seen_email_tip' in dismiss_tip_cookies
        assert int(dismiss_tip_cookies['seen_email_tip'].value) == 2
