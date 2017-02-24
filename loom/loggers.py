import loom.options

import logging

from os.path import join, abspath


def make_logger(name, filename=None, null_logger=False,
                logger_level=loom.options.parser.logging_level,
                file_level=loom.options.parser.logging_file_level,
                stream_level=loom.options.parser.logging_out_level):
    logger = logging.getLogger(name)
    if logger_level is None:
        logger_level = logging.WARNING
    logger.setLevel(logger_level)
    if null_logger:
        logger.addHandler(logging.NullHandler())
        return logger
    if filename is None:
        filename = f'{name}.log'
    if file_level:
        if loom.options.parser.logging_prefix is not None:
            filename = join(abspath(loom.options.parser.logging_prefix), filename)
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(file_level)
        logger.addHandler(file_handler)
    if stream_level:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(stream_level)
        logger.addHandler(stream_handler)
    return logger


rest_connections = make_logger('rest_connections')
ws_connections = make_logger('ws_connections')
db_queries = make_logger('db_queries')
