from bs4 import BeautifulSoup
from lib.html_truncation import truncate_html

import pytest


@pytest.fixture
def no_html():
    return 'All work and no play makes Jack a dull boy. ' * 10


@pytest.fixture
def unordered_list():
    li = '<li>All work and no play makes Jack a dull boy. </li>'
    return '<ul>{}</ul>'.format(li * 10)


class WhenHTMLTextIsLongerThanSpecifiedMax(object):

    def it_truncates_text_ignoring_tags_whole_words_to_max(self, no_html):
        assert len(truncate_html(no_html, 250)) == 246

    def it_truncates_html_keeping_well_formedness(self, unordered_list):
        truncated = truncate_html(unordered_list, 250)
        soup = BeautifulSoup(truncated, 'html.parser')
        assert len(soup.text) == 246
        assert len(soup.find_all('ul')) == 1
        assert len(soup.find_all('li')) == 6

    def it_appends_an_ellipsis_to_truncated_text(self, no_html):
        assert truncate_html(no_html, 250, end='...').endswith('...')
