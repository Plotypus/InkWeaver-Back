from . import handlers

ROUTES = [
    (r'/ws',        handlers.websockets.LoomHandler),
    (r'/api/login', handlers.rest.LoginHandler),
]


def get_routes():
    return ROUTES.copy()


def install_demo_endpoint(demo_db_data, endpoint=r'/ws/demo'):
    demo_endpoint = (endpoint, handlers.websockets.DemoHandler, dict(demo_db_data=demo_db_data))
    ROUTES.append(demo_endpoint)
