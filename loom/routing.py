from . import handlers

ROUTES = [
    (r'/ws',        handlers.websockets.LoomHandler),
    (r'/ws/demo',   handlers.websockets.DemoHandler),
    (r'/api/login', handlers.rest.LoginHandler),
]
