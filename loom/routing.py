from . import handlers

ROUTES = [
    (r'/ws/echo',   handlers.websockets.EchoHandler),
    (r'/ws',        handlers.websockets.LoomHandler),
    (r'/api/login', handlers.rest.LoginHandler),
]
