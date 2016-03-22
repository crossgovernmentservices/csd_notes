#!/usr/bin/env python

from flask.ext.script import Manager

from app.factory import create_app


manager = Manager(create_app)


def run_tests(module=None, *args):
    import pytest
    argv = ['-q', '--flakes', '--mccabe', '--pep8', '--spec']

    if module:
        argv.extend(['--pyargs', module])

    if args:
        argv.extend(args)

    pytest.main(argv)


@manager.command
def test():
    run_tests('tests.spec')


@manager.command
def smoketest():
    run_tests('tests.smoke', '--start-live-server')


@manager.command
def all_tests():
    run_tests()


@manager.command
def coverage():
    run_tests('tests.spec', '--cov=app', '--cov-report=html')


if __name__ == '__main__':
    manager.run()
