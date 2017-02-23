#!/usr/bin/env python3

from loom import routing, session_manager
from loom.database import interfaces
from loom.options import parser

import ssl
import sys
import tornado.ioloop
import tornado.web

from tornado.httpserver import HTTPServer

# Check requirements.
required_version = (3, 6)
current_version = sys.version_info
if current_version < required_version:
    raise RuntimeError("Need at least Python version 3.6! Current version: {}.{}".format(current_version[0],
                                                                                         current_version[1]))


def start_server(db_interface, demo_db_host, demo_db_port, demo_db_prefix, port, routes, session_manager, ssl_crt,
                 ssl_key, login_origin):
    settings = {
        'db_interface':        db_interface,
        'demo_db_host':        demo_db_host,
        'demo_db_port':        demo_db_port,
        'demo_db_prefix':      demo_db_prefix,
        'cookie_secret':       generate_cookie_secret(),
        'session_cookie_name': 'loom_session',
        'session_manager':     session_manager,
        'login_origin':        login_origin,
    }
    app = tornado.web.Application(routes, **settings)
    if ssl_crt and ssl_key:
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(ssl_crt, ssl_key)
        server = HTTPServer(app, ssl_options=ssl_ctx)
    else:
        server = HTTPServer(app)
    server.listen(port)
    print("Starting server at {}:{}".format('localhost', port))
    print("Using database at {}:{}".format(app.settings['db_interface'].client.host,
                                           app.settings['db_interface'].client.port))
    if app.settings['login_origin']:
        print("Accepting connections from {}".format(app.settings['login_origin']))
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


if __name__ == '__main__':
    parser.parse_options()

    demo_db_host = parser.demo_db_host if parser.demo_db_host else parser.db_host
    demo_db_port = parser.demo_db_port if parser.demo_db_port else parser.db_port
    demo_db_data = parser.demo_db_data

    if demo_db_data is not None:
        routing.install_demo_endpoint(demo_db_data)

    session_manager = session_manager.SessionManager()

    # Ensure either both or neither of the authentication arguments are given.
    if parser.db_user and not parser.db_pass:
        print("Cannot authenticate without password.")
        sys.exit(1)
    if parser.db_pass and not parser.db_user:
        print("Cannot authenticate without username.")
        sys.exit(1)

    interface = interfaces.MongoDBTornadoInterface(parser.db_name, parser.db_host, parser.db_port, parser.db_user,
                                                   parser.db_pass)

    start_server(interface, demo_db_host, demo_db_port, parser.demo_db_prefix, parser.port, routing.get_routes(),
                 session_manager, parser.ssl_crt, parser.ssl_key, parser.login_origin)
