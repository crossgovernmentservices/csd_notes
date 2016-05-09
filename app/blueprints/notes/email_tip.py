# -*- coding: utf-8 -*-
"""
EmailTip controls the tip box shown at the top of the notes list page
"""

from flask import after_this_request, current_app, request


class EmailTip(object):

    def __init__(self):
        self._times_seen = None
        self.set_template_context()

    @property
    def times_seen(self):
        if self._times_seen is None:
            self._times_seen = int(request.cookies.get('seen_email_tip', 0))

        return self._times_seen

    @times_seen.setter
    def times_seen(self, value):
        self._times_seen = value
        after_this_request(self.set_cookie)

    @property
    def visible(self):
        return self.times_seen < 2

    def incr_times_seen(self):
        if self.visible:
            self.times_seen += 1

    def set_cookie(self, response):
        response.set_cookie('seen_email_tip', str(self.times_seen))
        return response

    def set_template_context(self):
        current_app.jinja_env.globals['email_tip_visible'] = self.visible
