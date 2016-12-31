from loom import database, routing

import tornado.ioloop
import tornado.web

from tornado.options import define as define_option, options, parse_command_line as parse_options

define_option('port', default=8080, help='run on the given port', type=int)
define_option('db-host', default='localhost', help='address of the MongoDB server', type=str)
define_option('db-port', default=27017, help='MongoDB connection port', type=int)
define_option('db-collection', default='inkweaver', help='collection to use in the database', type=str)


def start_server(db_client, port, routes):
    settings = {'db_client': db_client}
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


if __name__ == '__main__':
    parse_options()

    client = database.LoomMongoDBMotorTornadoClient(options.db_collection, options.db_host, options.db_port)

    start_server(client, options.port, routing.ROUTES)
