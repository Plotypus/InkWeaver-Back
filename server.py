from loom import routing
from loom.database import interfaces

import tornado.ioloop
import tornado.web

from tornado.options import define as define_option, options, parse_command_line as parse_options

define_option('port', default=8080, help='run on the given port', type=int)
define_option('db-host', default='localhost', help='address of the MongoDB server', type=str)
define_option('db-port', default=27017, help='MongoDB connection port', type=int)
define_option('db-name', default='inkweaver', help='name of the database in MongoDB', type=str)


def start_server(db_interface, port, routes):
    settings = {
        'db_interface':  db_interface,
        'cookie_secret': generate_cookie_secret()
    }
    app = tornado.web.Application(routes, **settings)
    app.listen(port)
    print("Starting server at {}:{}".format('localhost', port))
    print("Using database at {}:{}".format(app.settings['db_client'].host, app.settings['db_client'].port))
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
    parse_options()

    interface = interfaces.MongoDBTornadoInterface(options.db_name, options.db_host, options.db_port)

    start_server(interface, options.port, routing.ROUTES)
