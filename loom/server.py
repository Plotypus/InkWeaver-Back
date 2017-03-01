from loom import routing
from loom.database.interfaces import MongoDBTornadoInterface
from loom.dispatchers import LAWProtocolDispatcher
from loom.routers import Router
from loom.session_manager import SessionManager

import base64
import ssl
import tornado.ioloop
import tornado.web

from os import urandom
from tornado.httpserver import HTTPServer

class LoomServer:
    def __init__(self, interface=None, session_manager=None, routes=None, dispatcher=None, router=None):
        self._interface = interface
        self._session_manager = session_manager
        self._routes = routes
        self._dispatcher = dispatcher
        self._router = router

    def create_db_interface(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        self._interface = MongoDBTornadoInterface(db_name, db_host, db_port, db_user, db_pass)

    def create_dispatcher(self):
        self._dispatcher = LAWProtocolDispatcher(self._interface)

    def create_router(self):
        self._router = Router(self._interface)

    def install_demo_endpoint(self, demo_db_data_file):
        routing.install_demo_endpoint(demo_db_data_file)

    def start_server(self, demo_db_host, demo_db_port, demo_db_prefix, port, ssl_cert, ssl_key, login_origin):
        if self._interface is None:
            raise RuntimeError("cannot start server without creating a database interface")
        if self._dispatcher is None:
            self.create_dispatcher()
        if self._router is None:
            self.create_router()
        session_manager = self._session_manager if self._session_manager is not None else SessionManager()
        routes = self._routes if self._routes is not None else routing.get_routes()
        settings = {
            'router':              self._router,
            'demo_db_host':        demo_db_host,
            'demo_db_port':        demo_db_port,
            'demo_db_prefix':      demo_db_prefix,
            'cookie_secret':       self._generate_cookie_secret(),
            'session_cookie_name': 'loom_session',
            'session_manager':     session_manager,
            'login_origin':        login_origin,
        }
        app = tornado.web.Application(routes, **settings)
        if ssl_cert and ssl_key:
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(ssl_cert, ssl_key)
            server = HTTPServer(app, ssl_options=ssl_context)
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
