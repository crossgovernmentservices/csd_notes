# Civil Service Digital Performance Review Notes App

[![Build Status](https://travis-ci.org/crossgovernmentservices/csd-notes.svg)](https://travis-ci.org/crossgovernmentservices/csd-notes)


## Requirements

- Python 3
- Ruby 2.2.0 (for `govuk_template`)
- PhantomJS (for UI testing)
- Dex (see [Setting up Dex locally](#setting-up-dex-locally))
- PostgreSQL 9.4


## Quickstart

1. Clone this repository and cd to the working directory

2. Install the requirements listed above if you don't have them already

3. `mkvirtualenv --python=/path/to/python3 <appname>`

4. `pip install -r requirements.txt`

5. `python manage.py install_all_govuk_assets`

6. `createdb notes`

7. `python manage.py db upgrade`

8. `python manage.py runserver`


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


## Setting up Dex locally

OK, this is a little long-winded:

1. Find your Google ID number

  1. Browse to [Google's OAuth 2 playground](https://accounts.google.com/o/oauth2/auth?redirect_uri=https://developers.google.com/oauthplayground&response_type=code&client_id=407408718192.apps.googleusercontent.com&scope=email)

  2. Click on `Exchange authorization code for tokens`

  3. Paste `https://www.googleapis.com/oauth2/v2/userinfo` into the `Request URI` field and `Send the request`

  4. Make a note of the `id` field in the JSON data at the bottom of the right hand side of the page

2. Get a Google client id and client secret

  1. If you do not already have one, [create a Google APIs project](https://console.developers.google.com/project)

  2. Go to `Credentials > OAuth consent screen`

  3. Add a `Product name`

  4. Select `Create Credentials > OAuth client ID`

  5. Select `Web application`, enter `http://127.0.0.1:5556/auth/google/callback` into `Authorized redirect URIs`

  6. Make a note of the `Client ID` and `Client secret` values near the top of the page

  7. Click `Save`

3. Build Dex
  1. Run
    ```sh
    GOPATH="$(pwd)/go"
    mkdir -p go/src/github.com/coreos
    cd go/src/github.com/coreos
    git clone https://github.com/coreos/dex
    cd dex
    ```

  2. Paste the following into `static/fixtures/client.json`:
    ```json
    [
      {
        "id": "notes-app",
        "secret": "c2VjcmV0ZQ==",
        "redirectURLs": ["http://localhost:5000/callback"]
      }
    ]
    ```

  3. Paste the following into `static/fixtures/emailer.json`:
    ```json
    {
      "type": "fake"
    }
    ```

  4. Paste the following into `static/fixtures/users.json`, replacing `YOUR_ID` with your Google ID number as found in step 1, and YOUR_EMAIL and YOUR_NAME with your email address and name, respectively
    ```json
    [
      {
        "id": "YOUR_ID",
        "email": "YOUR_EMAIL@digital.cabinet-office.gov.uk",
        "displayName": "YOUR_NAME",
        "password": "password",
        "remoteIdentities": [
          {
            "connectorId": "google",
            "id": "YOUR_ID"
          }
        ]
      }
    ]
    ```

  5. Paste the following into `static/fixtures/connectors.json`, replacing CLIENT_ID and CLIENT_SECRET with the Client ID and Client secret you obtained in step 2
    ```json
    [
      {
        "type": "oidc",
        "id": "google",
        "issuerURL": "https://accounts.google.com",
        "clientID": "CLIENT_ID",
        "clientSecret": "CLIENT_SECRET"
      }
    ]
    ```
  6. Run `bin/dex-worker --no-db --enable-registration`

1. Set up the app as per README instructions, but set the following environment variables before you run it:
    ```sh
    export DEX_APP_CLIENT_ID="notes-app"
    export DEX_APP_CLIENT_SECRET="c2VjcmV0ZQ=="
    export DEX_APP_DISCOVERY_URL="http://127.0.0.1:5556"
    python manage.py runserver
    ```

2. Browse to [http://localhost:5000/notes](notes page)

3. Be redirected to Dex's login page and click on `Log in with Google`

4. (Maybe) be redirected to Google's login page - sign in

5. Be redirected to the notes app list page, and see your name next to the `Sign out` link near the top of the page
