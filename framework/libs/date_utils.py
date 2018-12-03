#!/usr/bin/env python
# encoding: utf-8

import time
from datetime import datetime

DEFAULT_DT = datetime.strptime("1970-1-1", "%Y-%m-%d")

MINU_SEC = 60
HOUR_SEC = MINU_SEC * 60
DAY_SEC = 24 * HOUR_SEC
MON_SEC = DAY_SEC * 30
YEAR_SEC = 365 * DAY_SEC


def now_str():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def to_second_stamp(stamp):
    stamp = str(int(stamp))
    if len(stamp) > 10:
        stamp = stamp[:10]
        return stamp
    return int(stamp)


class DateTime(datetime):
    ''' Calculate datetime object '''

    def get_relate_seconds(self):
        delt = self - DEFAULT_DT
        total_seconds = delt.days * DAY_SEC
        total_seconds += delt.seconds
        return total_seconds

    def build_dt(self, s):
        return self.utcfromtimestamp(s)

    def add_days(self, days):
        total_seconds = self.get_relate_seconds()
        total_seconds += days * DAY_SEC
        return self.build_dt(total_seconds)

    def add_hours(self, hours):
        total_seconds = self.get_relate_seconds()
        total_seconds += hours * HOUR_SEC
        return self.build_dt(total_seconds)

    def add_minutes(self, m):
        total_seconds = self.get_relate_seconds()
        total_seconds += m * MINU_SEC
        return self.build_dt(total_seconds)

    def add_seconds(self, s):
        total_seconds = self.get_relate_seconds()
        total_seconds += s
        return self.build_dt(total_seconds)


def total_seconds(start, end):
    dt = end - start
    return dt.days * (60 * 60 * 24) + dt.seconds  # dt.microseconds


def str2stamp(string, fmt="%Y-%m-%d %H:%M:%S"):
    ''' Can't format the date before 1970-1-1 '''
    return time.mktime(time.strptime(string, fmt))


def stamp2str(stamp, fmt="%Y-%m-%d %H:%M:%S"):
    return time.strftime(fmt, time.localtime(stamp))


def str2obj(string, fmt="%Y-%m-%d %H:%M:%S", _type='datetime'):
    if _type == 'datetime':
        # import pdb;pdb.set_trace()
        _t = str2stamp(string, fmt)
        return DateTime.fromtimestamp(_t)
    elif _type == 'time':
        _t = str2stamp(string, fmt)
        return time.gmtime(_t)
    # return datetime.strptime(string, fmt)


def obj2str(obj, fmt="%Y-%m-%d %H:%M:%S"):
    return obj.strftime(fmt)


def stamp2obj(stamp, tz=8):
    return datetime.fromtimestamp(stamp)


def obj2stamp(obj, fmt="%Y-%m-%d %H:%M:%S"):
    if isinstance(obj, time.struct_time):
        return time.mktime(obj)
    if isinstance(obj, datetime):
        string = obj.strftime(fmt)
        return time.mktime(time.strptime(string, fmt))


##############################################################

import sys, re


# 将计时器"时:分:秒"字符串转换为秒数间隔
def time2itv(sTime):
    ''' 不合约定的参数： "12:34:95"  "sfa123"  4404855  '''

    p = "^([0-9]+):([0-5][0-9]):([0-5][0-9])$"
    cp = re.compile(p)
    try:
        mTime = cp.match(sTime)
    except TypeError:
        return "[InModuleError]:time2itv(sTime) invalid argument type"

    if mTime:
        t = map(int, mTime.group(1, 2, 3))
        return 3600 * t[0] + 60 * t[1] + t[2]
    else:
        return "[InModuleError]:time2itv(sTime) invalid argument value"


# 将秒数间隔转换为计时器"时:分:秒"字符串
def itv2time(iItv):
    ''' 不合约定的参数: "451223"  "1223:34:15" '''

    if type(iItv) == type(1):
        h = iItv / 3600
        sUp_h = iItv - 3600 * h
        m = sUp_h / 60
        sUp_m = sUp_h - 60 * m
        s = sUp_m
        return ":".join(map(str, (h, m, s)))
    else:
        return "[InModuleError]:itv2time(iItv) invalid argument type"


if __name__ == "__main__":
    _ID = "2015-1-1"
    fmt = "%Y-%m-%d %H:%M:%S"
    print 'str2stamp', str2stamp(_ID, fmt="%Y-%m-%d")
    # print datetime.strptime("2007-03-04 21:08:12", "%Y-%m-%d %H:%M:%S")
    print 'stamp2str', stamp2str(str2stamp(_ID, fmt="%Y-%m-%d"))
    print 'str2obj', str2obj("1979-1-1", fmt="%Y-%m-%d").day
    print 'obj2str', obj2str(datetime.now(), fmt="%Y-%m-%d")
    print 'stamp2obj', stamp2obj(time.time())
    print 'obj2stamp', obj2stamp(time.localtime())
    print 'obj2stamp', obj2stamp(datetime.now())
    print '*' * 80

    oneday = '2015-01-01 11:01:59'
    print str2obj(oneday).add_days(12)





