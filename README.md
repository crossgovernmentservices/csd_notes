# Civil Service Digital Performance Review Notes App

[![Build Status](https://travis-ci.org/crossgovernmentservices/csd-notes.svg)](https://travis-ci.org/crossgovernmentservices/csd-notes)


## Requirements

- Python 3


## Quickstart

1. Clone this repository and cd to the working directory

2. Install the requirements listed above if you don't have them already

3. `mkvirtualenv --python=/path/to/python3 <appname>`

4. `pip install -r requirements.txt`

5. `python manage.py runserver`


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

### Configuration

You may add local overrides to configuration in `app/config/local.py`, which is
not stored in version control.


## Deployment

### Configuration

The app looks for a Python module named in the `SETTINGS` environment variable.
For example, to use the included production configuration module, set the
`SETTINGS` environment variable to `app.config.production`


