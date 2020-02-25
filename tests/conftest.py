import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    # tempfile.mkstemp() creates and opens a temporary file, returning the file object and the path to it.
    # The DATABASE path is overridden so it points to this temporary path instead of the instance folder.
    # After setting the path, the database tables are created and the test data is inserted.
    # After the test is over, the temporary file is closed and removed.

    app = create_app({
        'TESTING': True,
        # TESTING tells Flask that the app is in test mode.
        # Flask changes some internal behavior so it’s easier to test, and other extensions can also use the flag to make testing them easier.
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()
# The client fixture calls app.test_client() with the application object created by the app fixture.
# Tests will use the client to make requests to the application without running the server.


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
# The runner fixture is similar to client. app.test_cli_runner() creates a runner that can call the Click commands registered with the application.


# With the auth fixture, you can call auth.login() in a test to log in as the test user, which was inserted as part of the test data in the app fixture.
# The register view should render successfully on GETselfselfself.
# On POST with valid form data, it should redirect to the login URL and the user’s data should be in the database.
# Invalid data should display error messages.
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
