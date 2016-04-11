# Civil Service Digital Performance Review Notes App

[![Build Status](https://travis-ci.org/crossgovernmentservices/csd-notes.svg)](https://travis-ci.org/crossgovernmentservices/csd-notes)


## Requirements

- Python 3
- Ruby 2.2.0 (for `govuk_template`)
- PhantomJS (for UI testing)


## Quickstart

1. Clone this repository and cd to the working directory

2. Install the requirements listed above if you don't have them already

3. `mkvirtualenv --python=/path/to/python3 <appname>`

4. `pip install -r requirements.txt`

5. `python manage.py install_all_govuk_assets`

6. `python manage.py db upgrade`

7. `python manage.py runserver`


## Tests

To run all tests:
```
python manage.py test
```

To run only fast unit tests:
```
python manage.py test spec
```

To run only smoke tests:
```
python manage.py test smoke
```

To run only UI tests:
```
python manage.py test ui
```

To generate HTML coverage reports (in the `htmlcov` directory)
```
python manage.py test coverage
```


## Deployment

### Configuration

The app looks for a `SETTINGS` environment variable on start up.  To retrieve
configuration values from AWS DynamoDB using credstash, set the `SETTINGS`
environment variable to `AWS`.  Otherwise, the default configuration is used,
which fetches values from the environment.

<dl>
  <dt><code>DEBUG</code></dt>
  <dd>(default: True) Run the app in debug mode, with exceptions triggering
  the online debugger</dd>

  <dt><code>SECRET_KEY</code></dt>
  <dd>(default: randomly generated) The key used to encypt session cookies and
  possibly other encrypted data. The default changes on server restart, so
  sessions will be lost unless a constant value is used</dd>

  <dt><code>DATABASE_URL</code></dt>
  <dd>(default: <code>sqlite:///development.db</code>) The URL for the database.
  This can include a username and password</dd>
</dl>
