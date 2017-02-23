import argparse


class OptionParser:
    _DEFAULTS = {
        'port':           8080,
        'db_name':        'inkweaver',
        'db_host':        'localhost',
        'db_port':        27017,
        'demo_db_prefix': 'demo-db',
        'login_origin':   'https://localhost:3000',
    }

    _TYPES = {
        'port':         int,
        'db_port':      int,
        'demo_db_port': int,
    }

    _ARGUMENTS = [
        ('--config',            'a config file to load default options from'),
        ('--port',              'run on the given port'),
        ('--db-name',           'name of the database in MongoDB'),
        ('--db-host',           'address of the MongoDB server'),
        ('--db-port',           'MongoDB connection port'),
        ('--db-user',           'user for MongoDB authentication'),
        ('--db-pass',           'password for MongoDB authentication'),
        ('--demo-db-host',      'the host for creating demonstration databases; defaults to --db-host'),
        ('--demo-db-port',      'the port for creating demonstration databases; defaults to --db-port'),
        ('--demo-db-prefix',    'the prefix for all databases created for the demo'),
        ('--demo-db-data',      'the data file to load demo data from'),
        ('--ssl-cert',          'the SSL cert file'),
        ('--ssl-key',           'the SSL key file'),
        ('--login-origin',      'hostname to configure CORS during login'),
    ]

    def _fix_option_name(self, name):
        return name.strip().replace('-', '_')

    def _get_option_type(self, name):
        return self._TYPES.get(self._fix_option_name(name), str)

    def __init__(self):
        self._options = {}
        self._parser = argparse.ArgumentParser()
        for argument in self._ARGUMENTS:
            self._parser.add_argument(argument[0], help=argument[1], type=self._get_option_type(argument[0]))

    def __getattr__(self, item):
        try:
            return self._options[item]
        except KeyError:
            return None

    def _parse_config_file(self, config_file: str):
        file_options = {}
        with open(config_file) as cf:
            for line in cf:
                if line:
                    left, right = line.split(':', 1)
                    key = self._fix_option_name(left)
                    # Cast value to appropriate type.
                    val_type = self._get_option_type(key)
                    val = val_type(right.strip())
                    file_options[key] = val
        return file_options

    def parse_options(self, args=None):
        self._options = {}
        if args is None:
            import sys
            args = sys.argv[1:]  # Disregard the first item, which is just the name of the program.
        parsed_args = self._parser.parse_args(args)
        # Check if the user specified a config file. If they did, read that first so CLI arguments take precedence.
        if parsed_args.config is not None:
            config_args = self._parse_config_file(parsed_args.config)
            self._options.update(config_args)
        for key, val in vars(parsed_args).items():
            if key not in self._options or val is not None:
                self._options[key] = val
        for default_arg, default_val in self._DEFAULTS.items():
            if getattr(self, default_arg) is None:
                self._options[default_arg] = default_val


# Provide a default, global OptionParser.
parser = OptionParser()
