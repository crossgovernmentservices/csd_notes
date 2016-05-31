from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Tag


competency_names = set([
    'Delivering Value for Money',
    'Seeing the Big Picture',
    'Changing and Improving',
    'Making Effective Decisions',
    'Leading and Communicating',
    'Collaborating and Partnering',
    'Building Capability for All',
    'Achieving Commercial Outcomes',
    'Managing a Quality Service',
    'Delivering at Pace'])


@pytest.fixture
def tags(db_session, test_user):

    def make_tag(name):
        tag = Tag(name=name, author=test_user)
        db_session.add(tag)
        db_session.commit()
        return tag

    return list(map(make_tag, ['foo', 'bar', 'quux']))


@pytest.fixture
def response(client, logged_in):
    return client.get(url_for('notes.tags'))


@pytest.fixture
def soup(response):
    return BeautifulSoup(response.get_data(as_text=True), 'html.parser')


class WhenOnTheManageTagsPage(object):

    def it_shows_all_user_tags_in_a_section(self, tags, soup):
        tag_lists = soup.find_all(class_='tag-list-block')
        assert len(tag_lists) == 2

        user_tags = tag_lists[0]
        assert user_tags.previous_sibling.previous_sibling.text == 'Your tags'

        user_tags = user_tags.find_all(class_='note-tag')
        assert len(user_tags) == 3

    def it_shows_all_default_tags_in_a_section(self, tags, soup):
        tag_lists = soup.find_all(class_='tag-list-block')
        assert len(tag_lists) == 2

        default_tags = tag_lists[1]
        title = default_tags.previous_sibling.previous_sibling.text
        assert title == 'Default tags'

        default_tags = default_tags.find_all(class_='note-tag')
        assert len(default_tags) == 10

        default_tags = set(map(lambda x: x.find('a').text, default_tags))
        assert competency_names.issubset(default_tags)
