#coding:utf-8
import logging
logger = logging.getLogger(__name__)

from bs4 import BeautifulSoup as bs
import ast
import json
from gevent.local import local


class Extract(object):
    pass


class bs_ctx(object):

    def __init__(self, source, parser):
        self.local_data = local()

        self.source = source
        self.parser = parser

    def __enter__(self):
        self.soup = bs(self.source, self.parser)
        self.local_data.soup = self.soup
        return self.soup

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.soup.clear(True)
        self.local_data.soup.clear(True)


class Parser(object):

    def __init__(self, src=None):
        self.source = src
        self.bs = None

    def parse_dom(self, parser='html.parser'):
        # self.bs = bs(self.source, parser)
        # return self.bs
        return bs_ctx(self.source, parser)

    def parse_js(self, src, start=None, end=None, strip='{"'):
        """
        :param src:
        Example:
            '<script>var THATDATA={"a": 1};</script>'

        :param start:  Example: 'THATDATA={"'
        :param end:    Example: '};'
        :return:
        """
        start_index = src.find(start)

        src = src[start_index:]
        end_index = src.find(end) + 1

        src = src[:end_index]
        src = src.lstrip(start.rstrip(strip))

        # res = ast.literal_eval(src)
        res = json.loads(src)

        return res

    
def main():

    def test():
        html = '<script> var adsf={"a": 1};</script>'
        parser = Parser(html)

        # dom = parser.parse_dom()
        print parser.parse_js(html, 'adsf={"', '};')

    test()






