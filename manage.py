#!/usr/bin/env python

import glob
import os
import shutil
import subprocess
from tempfile import TemporaryDirectory
import urllib
import zipfile

from flask.ext.migrate import MigrateCommand
from flask.ext.script import Manager
import pytest

from app.factory import create_app


manager = Manager(create_app)
manager.add_command('db', MigrateCommand)


def run_tests(module=None, *args):
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


def download(url, to=None):
    print('wget {} -O {}'.format(url, to))
    urllib.request.urlretrieve(url, to)


def extract(filename, to=None):
    print('unzip {} {}'.format(filename, to))
    with zipfile.ZipFile(filename) as zf:
        zf.extractall(to)


old_cwd = None


def pushd(path):
    global old_cwd
    old_cwd = os.getcwd()
    os.chdir(path)


def popd():
    if old_cwd:
        os.chdir(old_cwd)


def build_templates():
    subprocess.call(['bundle', 'install'])
    subprocess.call(['bundle', 'exec', 'rake', 'build:jinja'])


def mkdir_p(path):
    if not os.path.isdir(path):
        print('mkdir -p {}'.format(path))
        os.makedirs(path)
    return path


def move(src, to):
    print('mv {} {}'.format(src, to))
    for f in glob.glob(src):
        shutil.move(f, to)


def rmdir(path):
    if os.path.isdir(path):
        print('rmdir {}'.format(path))
        shutil.rmtree(path)


@manager.option('--app-dir', dest='app_dir', default='app')
@manager.option('--clean', dest='clean', default=None)
def install_govuk_template(app_dir, clean):

    dest_views = '{}/templates/govuk_template'.format(app_dir)
    dest_assets = '{}/static/govuk_template'.format(app_dir)

    if clean:
        rmdir(dest_views)
        rmdir(dest_assets)

    with TemporaryDirectory() as download_dir:
        dest_zip = '{}/govuk_template.zip'.format(download_dir)
        unzip_dir = '{}/unzipped'.format(download_dir)

        download(
            'https://github.com/alphagov/govuk_template/archive/master.zip',
            to=dest_zip)

        extract(dest_zip, to=unzip_dir)

        pushd('{}/govuk_template-master'.format(unzip_dir))

        os.remove('.ruby-version')
        build_templates()

        popd()

        mkdir_p(dest_views)
        mkdir_p(dest_assets)

        pkg = '{}/govuk_template-master/pkg'.format(unzip_dir)

        move('{}/jinja_govuk_template*/assets'.format(pkg), to=dest_assets)
        move('{}/jinja_govuk_template*/views'.format(pkg), to=dest_views)


@manager.option('--app-dir', dest='app_dir', default='app')
@manager.option('--clean', dest='clean', default=None)
def install_govuk_elements(app_dir, clean):

    dest_dir = '{}/static/govuk_elements'.format(app_dir)

    if clean:
        rmdir(dest_dir)

    with TemporaryDirectory() as download_dir:

        dest_zip = '{}/govuk_elements.zip'.format(download_dir)
        unzip_dir = '{}/unzipped'.format(download_dir)

        download(
            'https://github.com/alphagov/govuk_elements/archive/master.zip',
            to=dest_zip)

        extract(dest_zip, to=unzip_dir)

        mkdir_p(dest_dir)

        move('{}/govuk_elements-master/public'.format(unzip_dir), to=dest_dir)


@manager.option('--app-dir', dest='app_dir', default='app')
@manager.option('--clean', dest='clean', default=None)
def install_govuk_frontend_toolkit(app_dir, clean):

    dest_dir = '{}/static/govuk_frontend_toolkit'.format(app_dir)

    if clean:
        rmdir(dest_dir)

    with TemporaryDirectory() as download_dir:

        dest_zip = '{}/govuk_frontend_toolkit.zip'.format(download_dir)
        unzip_dir = '{}/unzipped'.format(download_dir)

        download((
            'https://github.com/alphagov/govuk_frontend_toolkit/archive/'
            'master.zip'),
            to=dest_zip)

        extract(dest_zip, to=unzip_dir)

        mkdir_p(dest_dir)

        for path in ['images', 'javascripts', 'stylesheets']:
            move(
                '{}/govuk_frontend_toolkit-master/{}'.format(unzip_dir, path),
                to=dest_dir)


@manager.option('--app-dir', dest='app_dir', default='app')
@manager.option('--clean', dest='clean', default=None)
def install_all_govuk_assets(app_dir, clean):
    install_govuk_frontend_toolkit(app_dir, clean)
    install_govuk_elements(app_dir, clean)
    install_govuk_template(app_dir, clean)


if __name__ == '__main__':
    manager.run()
