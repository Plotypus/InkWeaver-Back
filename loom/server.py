from loom import routing
from loom.database.interfaces import MongoDBTornadoInterface
from loom.session_manager import SessionManager

import base64
import ssl
import tornado.ioloop
import tornado.web

from os import urandom
from tornado.httpserver import HTTPServer

class LoomServer:
    def __init__(self, interface=None, session_manager=None, routes=None):
        self._interface = interface
        self._session_manager = session_manager
        self._routes = routes

    def create_db_interface(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        self._interface = MongoDBTornadoInterface(db_name, db_host, db_port, db_user, db_pass)

    def install_demo_endpoint(self, demo_db_data_file):
        routing.install_demo_endpoint(demo_db_data_file)

    def start_server(self, demo_db_host, demo_db_port, demo_db_prefix, port, ssl_crt, ssl_key, login_origin):
        if self._interface is None:
            raise RuntimeError("cannot start server without creating a database interface")
        session_manager = self._session_manager if self._session_manager is not None else SessionManager()
        routes = self._routes if self._routes is not None else routing.get_routes()
        settings = {
            'db_interface':        self._interface,
            'demo_db_host':        demo_db_host,
            'demo_db_port':        demo_db_port,
            'demo_db_prefix':      demo_db_prefix,
            'cookie_secret':       self._generate_cookie_secret(),
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

    def _generate_cookie_secret(self, num_bytes=64):
        return base64.b64encode(urandom(num_bytes))


main_server = LoomServer()
