from loom import routing, session_manager
from loom.database import interfaces

import tornado.ioloop
import tornado.web

from tornado.options import define as define_option, options, parse_command_line as parse_options

# Check requirements.
import sys
required_version = (3, 6)
current_version = sys.version_info
if current_version < required_version:
    raise RuntimeError("Need at least Python version 3.6! Current version: {}.{}".format(current_version[0], current_version[1]))

DEFAULT_DB_NAME = 'inkweaver'
DEFAULT_DB_HOST = 'localhost'
DEFAULT_DB_PORT = 27017

define_option('port', default=8080, help='run on the given port', type=int)
define_option('db-name', default=DEFAULT_DB_NAME, help='name of the database in MongoDB', type=str)
define_option('db-host', default=DEFAULT_DB_HOST, help='address of the MongoDB server', type=str)
define_option('db-port', default=DEFAULT_DB_PORT, help='MongoDB connection port', type=int)


def start_server(db_interface, port, routes, session_manager):
    settings = {
        'db_interface':        db_interface,
        'cookie_secret':       generate_cookie_secret(),
        'session_cookie_name': 'loom_session',
        'session_manager':     session_manager,
    }
    app = tornado.web.Application(routes, **settings)
    app.listen(port)
    print("Starting server at {}:{}".format('localhost', port))
    print("Using database at {}:{}".format(app.settings['db_interface'].client.host, app.settings['db_interface'].client.port))
    print("Press ^C to quit.")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\b\bQuitting...")
    finally:
        tornado.ioloop.IOLoop.current().stop()


def generate_cookie_secret(num_bytes=64):
    import base64
    from os import urandom
    return base64.b64encode(urandom(num_bytes))


def get_tornado_interface(db_name=DEFAULT_DB_NAME, db_host=DEFAULT_DB_HOST, db_port=DEFAULT_DB_PORT):
    return interfaces.MongoDBTornadoInterface(db_name, db_host, db_port)


if __name__ == '__main__':
    parse_options()

    interface = get_tornado_interface(options.db_name, options.db_host, options.db_port)

    session_manager = session_manager.SessionManager()

    start_server(interface, options.port, routing.ROUTES, session_manager)
