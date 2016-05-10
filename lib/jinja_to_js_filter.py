# -*- coding: utf-8 -*-
"""
Jinja-to-js client side template compiler filter for flask-assets
"""

import jinja_to_js
from webassets.filter import Filter


class JinjaToJs(Filter):
    name = 'jinja-to-js'

    def input(self, _in, out, **kwargs):
        src = kwargs.get('source_path').replace('app/templates/', '')
        out.write(self._compile(src))

    def _compile(self, src):
        compiler = jinja_to_js.JinjaToJS('app/templates', src)
        return compiler.get_output()
