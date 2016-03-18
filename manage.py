#!/usr/bin/env python

from flask.ext.script import Manager

from app.factory import create_app


manager = Manager(create_app)


@manager.command
def test():
    import nose
    nose.main(argv=[''])


@manager.command
def functest():
    import nose
    nose.main(argv=['-m', 'tests/functests.py'])


if __name__ == '__main__':
    manager.run()
