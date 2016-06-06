import sys
import logging


storage_word = []

if sys.platform[:3].lower() == 'win':
    chardet = 'gb18030'
else:
    chardet = 'utf8'


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s]: %(message)s'))

    logger.addHandler(console)
    return logger



