#coding:utf-8
import logging
logger = logging.getLogger(__name__)
import json
from framework.system import chains
from framework.components.fetchers import fetcher
from framework.components.parsers import Parser


def pretty_format(dict_obj):
    return json.dumps(dict_obj, indent=4, sort_keys=True)


def dd(sth=''):
    print sth
    exit(0)

