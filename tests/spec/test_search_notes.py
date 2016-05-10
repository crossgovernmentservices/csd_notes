# -*- coding: utf-8 -*-
"""
Search tests
"""

from bs4 import BeautifulSoup
from flask import url_for
import pytest

from app.blueprints.notes.models import Note


@pytest.fixture
def some_notes(db_session, test_user):
    _notes = [
        'foo',
        'read', 'reader',
        'baz and bar', 'a bar', 'bar baz bar baz']
    return [Note.create(content=note, author=test_user) for note in _notes]


@pytest.fixture
def search(client):

    def do_search(term):
        response = client.get(url_for('notes.search', q=term))
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        return soup.find_all(class_='note')

    return do_search


@pytest.mark.usefixtures('logged_in')
class WhenUserSubmitsASearch(object):

    def it_shows_no_results_if_there_are_none(self, search):
        assert len(search('foo')) == 0

    def it_shows_matching_notes_if_found(self, some_notes, search):
        assert len(search('foo')) == 1

    def it_shows_results_matching_common_stem(self, some_notes, search):
        assert len(search('reading')) == 2

    def it_ignores_standard_stopwords(self, some_notes, search):
        assert len(search('and')) == 0
        assert len(search('and baz')) == 2
        assert len(search('a bar')) == 3

    def it_returns_any_note_containing_all_words(self, some_notes, search):
        assert len(search('bar baz')) == 2

    def it_orders_results_by_relevancy(self, some_notes, search):
        results = search('bar')

        def text(note):
            return note.find(itemprop='text').text.strip()

        assert text(results[0]) == 'bar baz bar baz'
        assert text(results[1]) == 'baz and bar'
        assert text(results[2]) == 'a bar'
