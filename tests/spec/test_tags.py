from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def tagged_note(db_session, test_user):
    note = Note.create(content='A tagged note', author=test_user)
    note.add_tag('foo')
    note.add_tag('bar')
    return note


@pytest.fixture
def create_note(client, logged_in):
    response = client.post(url_for('notes.add'), data={
        'content': 'A tagged note',
        'tags': 'test-tag, test-tag-2'},
        follow_redirects=True)

    html = response.get_data(as_text=True)

    return BeautifulSoup(html, 'html.parser')


@pytest.fixture
def before_update(client, logged_in, tagged_note):
    response = client.get(url_for('notes.edit', id=tagged_note.id))
    html = response.get_data(as_text=True)
    return BeautifulSoup(html, 'html.parser')


@pytest.fixture
def after_update(client, logged_in, tagged_note):
    response = client.post(
        url_for('notes.edit', id=tagged_note.id),
        data={
            'content': 'A tagged note',
            'tags': 'test-tag, test-tag2, foo'},
        follow_redirects=True)
    html = response.get_data(as_text=True)
    return BeautifulSoup(html, 'html.parser')


class WhenViewingANote(object):

    def it_has_a_list_of_tags(self, tagged_note):
        assert len(tagged_note.tags) == 2
        assert tagged_note.has_tag('foo')
        assert tagged_note.has_tag('bar')


class WhenCreatingATag(object):

    def it_strips_html_tags_from_the_user_input(self, db_session, tagged_note):
        tagged_note.add_tag('<script>alert("bad things")</script>')
        assert not tagged_note.has_tag('<script>alert("bad things")</script>')
        assert tagged_note.has_tag('alert("bad things")')


class WhenCreatingANote(object):

    def it_adds_specified_tags(self, create_note):
        tag_lists = create_note.find_all(class_='tag-list')
        assert len(tag_lists) == 1

        tags = tag_lists[0].find_all('li')
        assert len(tags) == 2

        assert 'test-tag' in tags[0].text


class WhenUpdatingANote(object):

    def it_adds_new_tags(self, before_update, after_update):
        tags = before_update.find_all(class_='tag-list')
        tags = tags[0].find_all('li')
        assert len(tags) == 2

        tags = after_update.find(class_='tag-list').find_all('li')
        assert len(tags) == 4
