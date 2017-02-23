#!/usr/bin/env python3

import sys

# Check version requirements.
required_version = (3, 6)
current_version = sys.version_info
if current_version < required_version:
    raise RuntimeError("requires Python >= 3.6; current version: {}.{}".format(current_version[0], current_version[1]))

# This is moved down so that if the user isn't using Python 3.6, nothing extra is ever loaded.
from loom.options import parser

parser.parse_options()

# This is moved down so that if the user specifies `--help` at the command line, they don't have to wait for all of the
# Tornado module to load (which is comparatively slow).
from loom.server import main_server

demo_db_host = parser.demo_db_host if parser.demo_db_host else parser.db_host
demo_db_port = parser.demo_db_port if parser.demo_db_port else parser.db_port
demo_db_data = parser.demo_db_data

if demo_db_data is not None:
    main_server.install_demo_endpoint(demo_db_data)

# Ensure either both or neither of the authentication arguments are given.
if parser.db_user and not parser.db_pass:
    print("Cannot authenticate without password.")
    sys.exit(1)
if parser.db_pass and not parser.db_user:
    print("Cannot authenticate without username.")
    sys.exit(1)

# Initialize the database interface.
main_server.create_db_interface(parser.db_name, parser.db_host, parser.db_port, parser.db_user, parser.db_pass)

# Start the server!
main_server.start_server(
    demo_db_host=demo_db_host,
    demo_db_port=demo_db_port,
    demo_db_prefix=parser.demo_db_prefix,
    port=parser.port,
    ssl_cert=parser.ssl_cert,
    ssl_key=parser.ssl_key,
    login_origin=parser.login_origin
)
