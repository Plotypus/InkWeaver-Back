import loom.options

import logging

from os.path import join, abspath


class LoomLogger:
    def __init__(self, name, filename=None, file_level=loom.options.parser.logging_file_level,
                 stream_level=loom.options.parser.logging_out_level, null_logger=False):
        log_name = 'loom'
        if name is not None:
            log_name += f'.{name}'
        self._logger = logging.getLogger(log_name)
        if null_logger:
            self._logger.addHandler(logging.NullHandler())
            return
        if filename is None:
            filename = f'{name}.log'
        if file_level:
            if loom.options.parser.logging_prefix is not None:
                filename = join(abspath(loom.options.parser.logging_prefix), filename)
            file_handler = logging.FileHandler(filename)
            file_handler.setLevel(file_level)
            self._logger.addHandler(file_handler)
        if stream_level:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(stream_level)
            self._logger.addHandler(stream_handler)

    def debug(self, message, *args, **kwargs):
        return self._logger.debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        return self._logger.info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        return self._logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        return self._logger.error(message, *args, **kwargs)

    def exception(self, message, *args, exc_info=True, **kwargs):
        return self._logger.exception(message, *args, exc_info=exc_info, **kwargs)

    def critical(self, message, *args, **kwargs):
        return self._logger.critical(message, *args, **kwargs)


_root_logger = LoomLogger(name=None, null_logger=True)

connections = LoomLogger('connections')
db_queries = LoomLogger('db_queries')
