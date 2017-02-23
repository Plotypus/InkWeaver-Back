import argparse


class OptionParser:
    _DEFAULTS = {
        'db_name':      'inkweaver',
        'db_host':      'localhost',
        'db_port':      27017,
        'login_origin': 'https://localhost:3000',
    }

    def __init__(self):
        self._options = {}
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument('--config',           help='a config file to load default options from')
        self._parser.add_argument('--port',             help='run on the given port')
        self._parser.add_argument('--db-name',          help='name of the database in MongoDB')
        self._parser.add_argument('--db-host',          help='address of the MongoDB server')
        self._parser.add_argument('--db-port',          help='MongoDB connection port')
        self._parser.add_argument('--db-user',          help='user for MongoDB authentication')
        self._parser.add_argument('--db-pass',          help='password for MongoDB authentication')
        self._parser.add_argument('--demo-db-host',     help='the host for creating demonstration databases; defaults to --db-host')
        self._parser.add_argument('--demo-db-port',     help='the port for creating demonstration databases; defaults to --db-port')
        self._parser.add_argument('--demo-db-prefix',   help='the prefix for all databases created for the demo')
        self._parser.add_argument('--demo-db-data',     help='the data file to load demo data from')
        self._parser.add_argument('--ssl-cert',         help='the SSL cert file')
        self._parser.add_argument('--ssl-key',          help='the SSL key file')
        self._parser.add_argument('--login-origin',     help='hostname to configure CORS during login')

    def __getattr__(self, item):
        try:
            return self._options[item]
        except KeyError:
            return None

    def parse_config_file(self, config_file: str):
        file_options = {}
        with open(config_file) as cf:
            for line in cf:
                if line:
                    left, right = line.split(':', 1)
                    key = left.strip()
                    val = right.strip()
                    file_options[key] = val
        self._options.update(file_options)

    def parse_options(self, args=None):
        if args is None:
            import sys
            args = sys.argv[1:]  # Disregard the first item, which is just the name of the program.
        parsed_args = self._parser.parse_args(args)
        # Check if the user specified a config file. If they did, read that first so CLI arguments take precedence.
        if parsed_args.config is not None:
            self.parse_config_file(parsed_args.config)
        self._options.update(vars(parsed_args))
        for default_arg, default_val in self._DEFAULTS:
            if getattr(self, default_arg) is None:
                self._options[default_arg] = default_val


# Provide a default, global OptionParser.
parser = OptionParser()
