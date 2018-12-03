#coding:utf-8
import logging
logger = logging.getLogger(__name__)

# from eventlet.green import urllib2
import StringIO
import cookielib
import gzip
import traceback
import urllib2

import os
import requests
import json
import zlib
import time
import base64
import errs
from requests import exceptions as reqeusts_execs

from framework.libs import utils
if utils.is_gevent_enabled():
    from gevent import sleep
else:
    from time import sleep


DEFAULT_TIMEOUT = 3
INCREASE_TIMEOUT = 3

DEFAULT_MAX_RETRY = 3

DEFAULT_ENGINE = 'urllib2'


class Gzip(object):

    def handle_cooke(self, resp):
        if resp.headers.get('Set-Cookie'):
            cookies = []

            from Cookie import SimpleCookie

            for k, v in resp.headers.items():
                if k == 'set-cookie':
                    cookie = SimpleCookie()
                    cookie.load(v)
                    print v
                    # import pdb;pdb.set_trace()
                    # for v in cookie._cookies.values():
                    #     for c in v.values():
                    #         for d in c.values():
                    #             cookies.append(d.name + '=' + d.value)
                    for v in cookie.values():
                        cookies.append(v.key + '=' + v.coded_value)

                    cookies = ';'.join(cookies)
                    if self.cookies is None:
                        self.cookies = cookies
                    else:
                        self.cookies = self.cookies + ';' + cookies
                    break
        else:
            self.cookies = None

    def handle_gzip(self, gzipped, ret):
        if gzipped:
            logger.info('gzipped with:' + str(gzipped))
            compressedstream = StringIO.StringIO(ret)
            gzipper = gzip.GzipFile(fileobj=compressedstream, mode='r')
            ret = gzipper.read()

        return ret


class FetchBase(object):
    def __init__(self, **kwargs):
        self.max_retry = kwargs.get('max_retry', DEFAULT_MAX_RETRY)
        self.code = 0
        self.cookies = None

    def get_cookie_by_sele(self, url):
        from selelib import SeleLib
        seleLib = SeleLib()
        cookies = seleLib.get_cookies(url)
        return cookies

    def to_json(self, string):
        return json.loads(string)

    def is_gzip(self, resp):
        gzipped = resp.headers.get('Content-Encoding')
        if gzipped:
            return True
        return False

    def _fetch(self, url, **kwargs):
        engine = kwargs.get('engine', DEFAULT_ENGINE)
        timeout = kwargs.get('timeout', 3)
        headers = kwargs.get('headers', {})

        if not headers:
            logger.warn(u'未设置headers, url:%s' % url)

        if kwargs.get('set_the_cookie'):
            cookies = self.get_cookie_by_sele(url)
            logger.info(cookies)
            headers['Cookie'] = cookies

        proxies = kwargs.get('proxies')
        logger.debug(str(proxies))

        if engine == DEFAULT_ENGINE:
            # req = urllib2.Request(url, headers=headers)
            # resp = urllib2.urlopen(req, timeout=timeout)
            handlers = []
            cookieJar = cookielib.CookieJar()
            handlers.append(urllib2.HTTPCookieProcessor(cookieJar))

            if proxies:
                handlers.append(urllib2.ProxyHandler(proxies))

            opener = urllib2.build_opener(*handlers)
            opener.addheaders = headers.items()
            resp = opener.open(url, timeout=timeout)

            self.resp = resp
            self.code = resp.code

            data = dict((cookie.name, cookie.value) for cookie in cookieJar)
            self.cookies = data
            ret = resp.read()

        else:
            args = kwargs.get('requests_args', {})
            if proxies:
                args['proxies'] = proxies

            resp = requests.get(
                url, headers=headers, timeout=timeout,
                # allow_redirects=False
                **args
            )

            self.resp = resp
            self.code = resp.status_code

            self.cookies = resp.cookies.get_dict()
            ret = resp.text

        if ret is None:
            logger.warn('Fetch None')

        return ret

    def fetch_data(self, url, **kwargs):
        return self._fetch(url, **kwargs)

    def fetch_json(self, url, **kwargs):
        data = self.fetch_data(url, **kwargs)
        try:
            return self.to_json(data)
        except Exception, e:
            logger.error(str(e))
            logger.error(data[:200])
            return {}

    def fetch_image(self, url, **kwargs):
        headers = kwargs.get('headers')
        timeout = kwargs.get('timeout', 5)
        cookie = kwargs.get('cookie')

        proxies = kwargs.get('proxies')

        handlers = []
        if cookie is not None:
            cookieJar = cookielib.CookieJar()
            handlers.append(urllib2.HTTPCookieProcessor(cookieJar))

        if proxies:
            handlers.append(urllib2.ProxyHandler(proxies))

        opener = urllib2.build_opener(*handlers)
        opener.addheaders = headers.items()
        resp = opener.open(url, timeout=timeout)

        content = resp.read()

        # if cookie is not None:
        #     opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
        #     req = urllib2.Request(url, headers=headers)
        #     resp = opener.open(req)
        #     content = resp.read
        #
        # else:
        #     req = urllib2.Request(url, headers=headers)
        #     resp = urllib2.urlopen(req, timeout=timeout)
        #
        #     # resp = urllib2.urlopen(url, timeout=kwargs.get('timeout', 3))
        #     content = resp.read()
        return content

    def fetch_ctl(self, fetch_method, url, **kwargs):
        max_retry = kwargs.get('max_retry') or self.max_retry
        timeout = kwargs.get('timeout', DEFAULT_TIMEOUT)
        # cookies = None
        max_retry = 1   # 将重试交给客户端
        for i in range(max_retry):
            kwargs['timeout'] = timeout
            try:
                res = fetch_method(url, **kwargs)
                return res

            except reqeusts_execs.ProxyError:
                logger.warn('ProxyError, retrying %d time, total:%d, url:%s' % (i+1, max_retry, url))
            except reqeusts_execs.SSLError:
                logging.warn('SSLError, retrying %d time, total:%d, url:%s' % (i+1, max_retry, url))
            except reqeusts_execs.ConnectionError:
                logging.warn('ConnectionError , retrying %d time, total:%d, url:%s' % (i+1, max_retry, url))
                # raise errs.SwitchNodeErr
            except reqeusts_execs.ReadTimeout:
                logging.warn('ReadTimeout , retrying %d time, total:%d, url:%s' % (i+1, max_retry, url))
            except urllib2.URLError:
                logging.warn('URLError , retrying %d time, total:%d, url:%s' % (i+1, max_retry, url))

            # except urllib2.HTTPError, e:
            #     logger.error(traceback.format_exc())
            #     if str(e).startswith('HTTP Error 302'):
            #         # import pdb;pdb.set_trace()
            #         # print self.resp.cookies
            #         pass

            # except Exception, e:
            #     logger.warn(traceback.format_exc())
            #     logger.warn(url)

            timeout += INCREASE_TIMEOUT

            sleep(0.5)

        self.code = 1

        logger.error(url)

        raise errs.FailedErr(traceback.format_exc())


def fetcher_main(url, kwargs={}, ret_cookie=False):
    fetchBase = FetchBase()
    # is_html = kwargs.has_key('is_html') and kwargs.pop('is_html') or None
    fetch_type = kwargs.get('fetch_type', 'html')
    if fetch_type == 'html':
        data = fetchBase.fetch_ctl(fetchBase.fetch_data, url, **kwargs)
    elif fetch_type == 'image':
        data = fetchBase.fetch_ctl(fetchBase.fetch_image, url, **kwargs)
    else:
        data = fetchBase.fetch_ctl(fetchBase.fetch_json, url, **kwargs)

    if ret_cookie:
        return data, fetchBase.cookies
    return data












