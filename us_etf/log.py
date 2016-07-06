import logging
from os.path import dirname, abspath, join
from logging.handlers import RotatingFileHandler


def get_logger(to_console=True, to_file=False):
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.INFO)
    filename = join(dirname(abspath(__file__)), 'log', 'etf.log')

    if to_console:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s'))

        _logger.addHandler(console)

    if to_file:
        file_handler = RotatingFileHandler(filename, backupCount=10, maxBytes=5 * 1024 * 1024)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s'))

        _logger.addHandler(file_handler)

    return _logger

logger = get_logger(to_console=False, to_file=True)
