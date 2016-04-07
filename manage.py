#!/usr/bin/env python

from flask.ext.assets import ManageAssets
from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
import pytest

from app.factory import create_app
from lib.govuk_assets import ManageGovUkAssets
from lib.travis_ci import travis_fold


manager = Manager(create_app)
manager.add_command('assets', ManageAssets())
manager.add_command('db', MigrateCommand)
manager.add_command('install_all_govuk_assets', ManageGovUkAssets())


def run_tests(module=None, *args):
    argv = []

    if module:
        argv.extend(['--pyargs', module])

    if args:
        argv.extend(args)

    return pytest.main(argv)


@manager.command
def test():
    return run_tests('tests.spec', '--spec')


@manager.command
def smoketest():
    return run_tests('tests.smoke', '--start-live-server')


@manager.command
def all_tests():
    return run_tests()


@manager.command
def coverage():
    return run_tests('tests.spec', '--cov=app', '--cov-report=html')


@manager.command
def build_and_test():
    with travis_fold('install_all_govuk_assets'):
        manager.handle('', ['install_all_govuk_assets', '--clean'])

    return test()


if __name__ == '__main__':
    manager.run()
