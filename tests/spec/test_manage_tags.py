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


def tag_section(soup, index):
    return soup.find_all(class_='tag-type-section')[index]


def tag_section_title(section):
    return section.find('h2').text.strip()


class WhenOnTheManageTagsPage(object):

    def it_shows_tags_in_4_sections(self, tags, soup):
        tag_sections = soup.find_all(class_='tag-type-section')
        assert len(tag_sections) == 4

        assert tag_section_title(tag_sections[0]).startswith('Your tags')
        assert tag_section_title(tag_sections[1]).startswith('Objective tags')
        assert tag_section_title(tag_sections[2]).startswith('Competency tags')
        assert tag_section_title(tag_sections[3]).startswith('System tags')

    @pytest.mark.parametrize('index,section', [
        (0, 'user'),
        (1, 'objective'),
        (2, 'competency'),
        (3, 'system')])
    def it_shows_tags_grouped_by_type(self, tags, soup, index, section):
        section_tags = tag_section(soup, index).find_all(class_='note-tag')
        assert len(section_tags) == len(tag_names[section])

        section_tag_names = set(map(lambda x: x.find('a').text, section_tags))
        assert set(tag_names[section]).issubset(section_tag_names)

    def it_allows_editing_user_tags_inline(self, tags, soup):
        form = tag_section(soup, 0).find('form')
        assert form['action'] == url_for('notes.tags')
        assert form['method'].lower() == 'post'


@pytest.fixture
def form_submit(client, tags, logged_in):
    return client.post(url_for('notes.tags'), data={
        'id': tags[0].id,
        'name': 'foofoo'})


@pytest.fixture
def follow_redirect(client, form_submit):
    return client.get(form_submit.headers['Location'])


@pytest.fixture
def edited_soup(follow_redirect):
    return BeautifulSoup(follow_redirect.get_data(as_text=True), 'html.parser')


class WhenEditingATagOnTheTagManagementPage(object):

    def it_redirects_to_the_management_page(self, form_submit):
        assert form_submit.status_code == 302
        assert url_for('notes.tags') in form_submit.headers['Location']

    def it_updates_the_tags_listed(self, tags, edited_soup):
        user_tags = tag_section(edited_soup, 0).find_all(class_='note-tag')
        assert len(user_tags) == 3

        user_tag_names = set(map(lambda x: x.find('a').text, user_tags))
        assert 'foofoo' in user_tag_names
        assert 'bar' in user_tag_names
        assert 'quux' in user_tag_names
