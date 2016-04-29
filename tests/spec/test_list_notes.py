from http.cookies import SimpleCookie

from bs4 import BeautifulSoup
from flask import url_for
from markupsafe import Markup
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def some_notes(db_session, test_user):
    content = '*Test note {{}}*\n{}'.format(
        'All work and no play makes Jack a dull boy\n' * 10)
    return [Note.create(content.format(i), test_user) for i in range(1, 4)]


@pytest.fixture
def response(client, some_notes, logged_in):
    return client.get(url_for('notes.list'))


@pytest.fixture
def soup(response):
    return BeautifulSoup(response.get_data(as_text=True), 'html.parser')


@pytest.fixture
def seen_twice_already(client, logged_in):
    client.set_cookie('localhost', 'seen_email_tip', '2')
    response = client.get(url_for('notes.list'))
    return response


@pytest.fixture
def seen_twice_already_soup(seen_twice_already):
    return BeautifulSoup(
        seen_twice_already.get_data(as_text=True),
        'html.parser')


@pytest.fixture
def dismiss_tip(client, logged_in):
    return client.get(url_for('notes.dismiss_tip'))


class WhenViewingNotesListPage(object):

    def it_lists_notes_in_reverse_chronological_order(self, soup):
        notes = soup.find_all(class_='note')
        assert len(notes) == 3

        def timestamp(note):
            return note.find(itemprop='dateModified')['data-timestamp']

        assert timestamp(notes[0]) >= timestamp(notes[1])
        assert timestamp(notes[1]) >= timestamp(notes[2])

    def it_renders_note_contents_as_markdown(self, soup):
        note = soup.find_all(class_='note')[0]
        assert len(note.find_all('em')) > 0

    def it_shows_only_the_first_250_characters_of_a_note(self, soup):
        notes = soup.find_all(class_='note')
        for note in notes:
            assert len(Markup(note.find(itemprop='text')).striptags()) <= 250

    def it_shows_the_email_tip(self, soup):
        tip = soup.find(class_='message-box')
        assert tip.find('a')['href'].startswith('mailto:')

    def it_sets_a_cookie_if_it_has_not_been_seen_twice_already(self, response):
        cookies = SimpleCookie()
        for header in response.headers.getlist('Set-Cookie'):
            cookies.load(header)
        assert 'seen_email_tip' in cookies
        assert int(cookies['seen_email_tip'].value) == 1

    def it_hides_the_email_tip_if_it_has_been_seen_twice_already(
            self, seen_twice_already_soup):
        tip = seen_twice_already_soup.find(class_='message-box')
        assert tip is None


class WhenDismissingTheEmailTip(object):

    def it_sets_a_cookie(self, dismiss_tip):
        cookies = SimpleCookie()
        cookies.load(dismiss_tip.headers.get('Set-Cookie'))
        assert 'seen_email_tip' in cookies
        assert int(cookies['seen_email_tip'].value) == 2
