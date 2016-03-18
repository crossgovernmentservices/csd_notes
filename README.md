# Civil Service Digital Performance Review Notes App

[![Build Status]()]()


## Requirements

- Python 3


## Quickstart

1. Clone this repository and cd to the working directory

2. Install the requirements listed above if you don't have them already

3. `mkvirtualenv --python=/path/to/python3 <appname>`

4. `pip install -r requirements.txt`

5. `python manage.py runserver`


## Tests

`python manage.py test`


## Development

### Configuration

You may add local overrides to configuration in `app/config/local.py`, which is
not stored in version control.


## Deployment

### Configuration

The app looks for a Python module named in the `SETTINGS` environment variable.
For example, to use the included production configuration module, set the
`SETTINGS` environment variable to `app.config.production`


