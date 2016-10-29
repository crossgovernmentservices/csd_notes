from app.factory import create_app
from app.middleware.basic_auth import BasicAuth


app = BasicAuth(create_app())
