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


suites = {
    'spec': ['--pyargs', 'tests.spec', '--spec'],
    'smoke': ['--pyargs', 'tests.smoke', '--start-live-server'],
    'ui': ['--pyargs', 'tests.ui', '--start-live-server'],
    'all': ['--start-live-server'],
    'coverage': ['--pyargs', 'tests.spec', '--cov=app', '--cov-report=html']
}


@manager.option(
    'suite', default='all', nargs='?', choices=suites.keys(),
    help='Specify test suite to run (default all)')
@manager.option('--spec', action='store_true', help='Output in spec style')
def test(spec, suite):
    """Runs tests"""
    args = []

    if spec:
        args.extend(['--spec'])

    if not suite:
        suite = 'all'

    args.extend(suites[suite])

    return pytest.main(args)


@manager.command
def build_and_test():
    with travis_fold('install_all_govuk_assets'):
        manager.handle('', ['install_all_govuk_assets', '--clean'])

    return test(spec=True, suite='spec')


if __name__ == '__main__':
    manager.run()
