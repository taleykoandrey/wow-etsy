import logging
from logging.handlers import RotatingFileHandler


filename = 'etsy.log'


class Etsy_Logger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name=name, level='INFO')

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(filename,
                                    maxBytes=8192 * 1024,
                                    backupCount=100,
                                    encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(filename, maxBytes=8192 * 1024, backupCount=100)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


elogger = get_logger()
