from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Tag


tag_names = {
    'competency': [
        'Delivering Value for Money',
        'Seeing the Big Picture',
        'Changing and Improving',
        'Making Effective Decisions',
        'Leading and Communicating',
        'Collaborating and Partnering',
        'Building Capability for All',
        'Achieving Commercial Outcomes',
        'Managing a Quality Service',
        'Delivering at Pace'],

    'objective': [
        'obj1',
        'obj2'],

    'system': [
        'development',
        'email',
        'feedback'],

    'user': [
        'foo',
        'bar',
        'quux']}


@pytest.fixture
def tags(db_session, test_user):

    def make_tag(name, ns=None):
        tag = Tag(name=name, author=test_user, namespace=ns)
        db_session.add(tag)
        db_session.commit()
        return tag

    return (
        list(map(make_tag, tag_names['user'])) +
        list(map(
            lambda x: make_tag(x, ns='Objective'),
            tag_names['objective'])))


@pytest.fixture
def response(client, logged_in):
    return client.get(url_for('notes.tags'))


@pytest.fixture
def soup(response):
    return BeautifulSoup(response.get_data(as_text=True), 'html.parser')


def tag_list(soup, index):
    return soup.find_all(class_='tag-list-block')[index].find_all(
        class_='note-tag')


def tag_list_title(tag_list):
    return tag_list.previous_sibling.previous_sibling.text.strip()


class WhenOnTheManageTagsPage(object):

    def it_shows_tags_in_4_sections(self, tags, soup):
        tag_lists = soup.find_all(class_='tag-list-block')
        assert len(tag_lists) == 4

        assert tag_list_title(tag_lists[0]).startswith('Your tags')
        assert tag_list_title(tag_lists[1]).startswith('Objective tags')
        assert tag_list_title(tag_lists[2]).startswith('Competency tags')
        assert tag_list_title(tag_lists[3]).startswith('System tags')

    @pytest.mark.parametrize('index,section', [
        (0, 'user'),
        (1, 'objective'),
        (2, 'competency'),
        (3, 'system')])
    def it_shows_tags_grouped_by_type(self, tags, soup, index, section):
        section_tags = tag_list(soup, index)
        assert len(section_tags) == len(tag_names[section])

        section_tag_names = set(map(lambda x: x.find('a').text, section_tags))
        assert set(tag_names[section]).issubset(section_tag_names)
