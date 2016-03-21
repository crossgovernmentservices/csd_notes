#!/usr/bin/env python

from flask.ext.script import Manager

from app.factory import create_app


manager = Manager(create_app)


@manager.command
def test():
    import nose
    nose.main(argv=['-m', 'tests.spec'])


@manager.command
def smoketest():
    import nose
    nose.main(argv=['-m', 'tests.smoke'])


@manager.command
def all_tests():
    import nose
    nose.main(argv=[''])


if __name__ == '__main__':
    manager.run()
