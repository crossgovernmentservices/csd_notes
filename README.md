# Civil Service Digital Performance Review Notes App

[![Build Status](https://travis-ci.org/crossgovernmentservices/csd-notes.svg)](https://travis-ci.org/crossgovernmentservices/csd-notes)


## Requirements

- Python 3
- Ruby 2.2.0 (for `govuk_template`)


## Quickstart

1. Clone this repository and cd to the working directory

2. Install the requirements listed above if you don't have them already

3. `mkvirtualenv --python=/path/to/python3 <appname>`

4. `pip install -r requirements.txt`

5. `python manage.py install_all_govuk_assets`

6. `python manage.py runserver`


## Tests

To run fast unit tests:
```
python manage.py test
```

To run smoke tests:
```
python manage.py smoketest
```

To run all tests:
```
python manage.py all_tests
```

To generate HTML coverage reports (in the `htmlcov` directory)
```
python manage.py coverage
```


## Development

### Requirements

If you depend on Python modules that are not needed in production (eg: ipython),
you may use a `local_requirements.txt` file which is not stored in version
control. Set the first line of this file to
```
-r requirements.txt
```
to add all the production dependencies. That way, you will only need to run
```
pip install -r local_requirements.txt
```
to install all requirements.


## Deployment

### Configuration

The app looks for a `SETTINGS` environment variable on start up.  To retrieve
configuration values from AWS DynamoDB using credstash, set the `SETTINGS`
environment variable to `AWS`.  Otherwise, the default configuration is used,
which fetches values from the environment.
