from database.database_session import global_init, create_session
from database.__all_models import User
from flask import Flask
from util import CONFIG

flask_app = Flask(__name__)


@flask_app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    global_init()
    flask_app.run("0.0.0.0")
