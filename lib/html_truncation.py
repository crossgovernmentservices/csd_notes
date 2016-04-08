# -*- coding: utf-8 -*-
"""
Truncate HTML to character limit, preserving well formedness
"""

from html.parser import HTMLParser


def truncate_words(text, max_chars, break_words=False, padding=0):
    """
    Truncate a string to max_chars, optionally truncating words
    """

    if break_words:
        return text[:-abs(max_chars - len(text)) - padding]

    words = []
    for word in text.split():
        length = sum(map(len, words)) + len(word) + len(words) - 1 + padding
        if length >= max_chars:
            break
        words.append(word)

    return ' '.join(words)


class TruncatingParser(HTMLParser):
    """
    Parse HTML and output a truncated version
    """

    def __init__(self, max_chars, end='', break_words=False):
        super(TruncatingParser, self).__init__()
        self.max_chars = max_chars
        self.num_chars = 0
        self.end = end
        self.break_words = break_words
        self.depth = 0
        self.odepth = 0
        self.output = ''

    @property
    def overflow(self):
        return self.num_chars + len(self.end) > self.max_chars

    def handle_starttag(self, tag, attrs):
        if self.overflow:
            self.odepth += 1

        else:
            self.depth += 1
            self.output_start(tag, attrs)

    def handle_endtag(self, tag):
        if self.depth > 0 and self.odepth == 0:
            self.depth -= 1
            self.output_end(tag)
        else:
            self.odepth -= 1

    def handle_startendtag(self, tag, attrs):
        if self.overflow:
            self.odepth += 1

        else:
            self.depth += 1

        if self.depth > 0 and self.odepth == 0:
            self.depth -= 1
            self.output_startend(tag, attrs)

        else:
            self.odepth -= 1

    def handle_data(self, data):
        self.num_chars += len(data)

        if self.overflow:
            overflow_chars = self.num_chars - self.max_chars + len(self.end)
            data = truncate_words(
                data,
                len(data) - overflow_chars,
                break_words=self.break_words,
                padding=len(self.end))

            if data:
                data += self.end

        self.output_data(data)

    def output_start(self, tag, attrs, self_closing=False):
        self.output += '<{}{}{}>'.format(
            tag,
            ' '.join('='.join(pair) for pair in attrs),
            ' /' if self_closing else '')

    def output_end(self, tag):
        self.output += '</{}>'.format(tag)

    def output_startend(self, tag, attrs):
        self.output_start(tag, attrs, self_closing=True)

    def output_data(self, data):
        if data:
            self.output += data


def truncate_html(html, max_chars, end='', break_words=False):
    """
    Truncate an HTML string to specified character limit, preserving
    well-formedness
    """

    parser = TruncatingParser(max_chars, end=end, break_words=break_words)
    parser.feed('<div>{}</div>'.format(html))
    return parser.output[5:-6]
