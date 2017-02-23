import argparse


class OptionParser:
    _DEFAULT_DB_NAME = 'inkweaver'
    _DEFAULT_DB_HOST = 'localhost'
    _DEFAULT_DB_PORT = 27017
    _DEFAULT_LOGIN_ORIGIN = 'https://localhost:3000'

    _OPTIONS = [
        {
            'name':    'config',
            'default': None,
            'help':    'a config file to load options from',
            'type':    str,
        },
        {
            'name':    'port',
            'default': 8080,
            'help':    'run on the given port',
            'type':    int,
        },
        {
            'name':    'db-name',
            'default': _DEFAULT_DB_NAME,
            'help':    'name of the database in MongoDB',
            'type':    str,
        },
        {
            'name':    'db-host',
            'default': _DEFAULT_DB_HOST,
            'help':    'address of the MongoDB server',
            'type':    str,
        },
        {
            'name':    'db-port',
            'default': _DEFAULT_DB_PORT,
            'help':    'MongoDB connection port',
            'type':    int,
        },
        {
            'name':    'db-user',
            'default': None,
            'help':    'user for MongoDB authentication',
            'type':    str,
        },
        {
            'name':    'db-pass',
            'default': None,
            'help':    'password for MongoDB authentication',
            'type':    str,
        },
        {
            'name':    'demo-db-host',
            'default': None,
            'help':    'the host for creating demonstration databases; defaults to --db-host',
            'type':    str,
        },
        {
            'name':    'demo-db-port',
            'default': None,
            'help':    'the port for creating demonstration databases; defaults to --db-port',
            'type':    int,
        },
        {
            'name':    'demo-db-prefix',
            'default': 'demo-db',
            'help':    'the prefix for all databases created for the demo',
            'type':    str,
        },
        {
            'name':    'demo-db-data',
            'default': None,
            'help':    'the data file to load demo data from',
            'type':    str,
        },
        {
            'name':    'ssl-crt',
            'default': None,
            'help':    'the ssl cert file',
            'type':    str,
        },
        {
            'name':    'ssl-key',
            'default': None,
            'help':    'the ssl key file',
            'type':    str,
        },
        {
            'name':    'login-origin',
            'default': _DEFAULT_LOGIN_ORIGIN,
            'help':    'hostname to configure CORS during login',
            'type':    str,
        },
    ]

    def __init__(self):
        self._options = {}
        self._parser = argparse.ArgumentParser()
        for option in self._OPTIONS:
            option['name'] = f"--{option['name']}"  # Add '--' to the front of the name.
            self._parser.add_argument(**option)

    def __getattr__(self, item):
        try:
            return self._options[item]
        except KeyError:
            raise AttributeError

    def parse_config_file(self, config_file: str):
        file_options = {}
        with open(config_file) as cf:
            for line in cf:
                if line:
                    left, right = line.split(':')
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


parser = OptionParser()
