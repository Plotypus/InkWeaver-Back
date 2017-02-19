#!/usr/bin/env python

import sys

from os.path import dirname

sys.path.append(dirname(dirname(__file__)))

from loom.data_processor import DataProcessor
from loom.database.interfaces import MongoDBAsyncioInterface

import asyncio


def main(jsonfile, db_name, db_user=None, db_pass=None, blind_override=False):
    if not blind_override:
        answer = input("This will drop the `{}` database... continue? [y/N] ".format(db_name))
        if not answer.lower().startswith('y'):
            print("Quitting...")
            return
        print("Continuing.")
    event_loop = asyncio.get_event_loop()
    interface = MongoDBAsyncioInterface(db_name, 'localhost', 27017)
    if db_user and db_pass:
        interface.authenticate_client(db_user, db_pass)
    processor = DataProcessor(interface)
    event_loop.run_until_complete(interface.client.drop_all_collections())
    event_loop.run_until_complete(processor.load_file(jsonfile))
    event_loop.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', help='Path to the data file.')
    parser.add_argument('--db-name', default='inkweaver', help='Name of the database you want to use.')
    parser.add_argument('--db-user', default=None, help='Username to authenticate MongoDB.')
    parser.add_argument('--db-pass', default=None, help='Password to authenticate MongoDB.')
    parser.add_argument('--no-ask', help='Do not ask for verification to dump existing database.',
                        action='store_true')
    args = parser.parse_args()

    # Ensure either both or neither of the authentication arguments are given.
    if args.db_user and not args.db_pass:
        print("Cannot authenticate without password.")
        sys.exit(1)
    if args.db_pass and not args.db_user:
        print("Cannot authenticate without username.")
        sys.exit(1)

    main(args.data_file, args.db_name, args.db_user, args.db_pass, args.no_ask)
