#coding:utf-8
import logging

FORMAT = '%(asctime)s [%(filename)s line:%(lineno)d] %(levelname)s\t%(message)s'

level_map = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


def initLog(level=logging.INFO):
    if isinstance(level, (str, unicode)):
        level = level_map[level]

    logging.basicConfig(level=level, format=FORMAT)
    return logging

