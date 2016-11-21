import loom.constants

import tornado.ioloop
import tornado.web

from tornado.options import define as define_option, options, parse_command_line as parse_options

define_option('port', default=8080, help='run on the given port', type=int)


def start_server(port):
    app = tornado.web.Application(loom.constants.ROUTES)
    app.listen(port)
    print("Starting server... press ^C to quit.")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\b\bQuitting...")
    finally:
        tornado.ioloop.IOLoop.current().stop()


if __name__ == '__main__':
    parse_options()
    start_server(options.port)
