#coding:utf-8
import sys
import socket
import logging
logger = logging.getLogger(__name__)

import random
import bisect

import time
import json
import datetime
from framework.common import constant


class Msg(dict):

    def __init__(self, *args, **kwargs):
        super(Msg, self).__init__(*args, **kwargs)
        self.dict = {
            'code': kwargs.get('code', constant.Code.success),
            'msg': kwargs.get('msg'),
            'data': kwargs.get('data'),
        }
        # self.dict_str = str(self.dict)
        for k, v in self.dict.items():
            setattr(self, k, v)

    def make(**kwargs):
        return

    def is_failed(self):
        if self.code == constant.Code.failed:
            return True
        return False

    def is_success(self):
        if self.code == constant.Code.success:
            return True
        return False

    def __str__(self):
        return str(self.dict)


def dummy_sleep_forever():
    while 1:
        time.sleep(3)


def dd(sth=''):
    print sth
    exit(0)


def format_exc_vars():
    exc_type, exc_value, tb = sys.exc_info()
    if tb is not None:
        prev = tb
        curr = tb.tb_next
        while curr is not None:
            prev = curr
            curr = curr.tb_next
        return prev.tb_frame.f_locals


def test_redis_conn(ip, port=6379):
    is_on = False
    s = socket.socket()
    try:
        s.connect((ip, port))
        is_on = True
    except Exception, e:
        logger.warn('Testing to reconnect')
    finally:
        s.close()

    return is_on


class CJsonEncoder(json.JSONEncoder):
    '''将时间类型数据转化成JSON'''
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # return obj.strftime('%m %d,%Y %H:%M:%S')
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def recur_get(dct, key_str, default=None, set_dict=False):
    if isinstance(key_str, (str, unicode)):
        keys = key_str.split('.')
    elif isinstance(key_str, (tuple, list)):
        keys = key_str

    tmpdct = dct
    for key in keys:
        if not tmpdct.has_key(key):
            # print u'%s key is not exists' % key
            if set_dict:
                tmpdct[key] = {}
            else:
                return default
        tmpdct = tmpdct[key]
    return tmpdct


def is_gevent_enabled():
    import socket, gevent.socket
    if socket.socket == gevent.socket.socket:
        return True
    return False


def sleep(seconds):
    if is_gevent_enabled():
        from gevent import sleep
        sleep(seconds)
    else:
        time.sleep(seconds)


def weight_choice(data):
    """TODO 是否存在泄漏?"""
    def _weight_choice(weight):
        """
        :param weight: list对应的权重序列
        :return:选取的值在原列表里的索引
        """
        weight_sum = []
        sum = 0
        for a in weight:
            sum += a
            weight_sum.append(sum)
        t = random.randint(0, sum - 1)
        return bisect.bisect_right(weight_sum, t)

    return data.keys()[_weight_choice(data.values())]


def main():
    print is_gevent_enabled()
