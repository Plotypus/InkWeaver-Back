#!/usr/bin/env python

import sys

from os.path import dirname

sys.path.append(dirname(dirname(__file__)))

from loom.data_processor import DataProcessor
from loom.database.interfaces import MongoDBAsyncioInterface

import asyncio


def main(jsonfile, db_name, blind_override=False):
    if not blind_override:
        answer = input("This will drop the `{}` database... continue? [y/N] ".format(db_name))
        if not answer.lower().startswith('y'):
            print("Quitting...")
            return
        print("Continuing.")
    event_loop = asyncio.get_event_loop()
    interface = MongoDBAsyncioInterface(db_name, 'localhost', 27017)
    processor = DataProcessor(interface)
    event_loop.run_until_complete(interface.client.drop_database())
    event_loop.run_until_complete(processor.load_file(jsonfile))
    event_loop.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', help='Path to the data file.')
    parser.add_argument('--db_name', default='inkweaver', help='Name of the database you want to use.')
    parser.add_argument('--no-ask', help='Do not ask for verification to dump existing database.',
                        action='store_true')
    args = parser.parse_args()

    main(args.data_file, args.db_name, args.no_ask)
