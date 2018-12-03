#coding:utf-8
import logging
logger = logging.getLogger(__name__)

import time
import gevent

from gevent.pool import Pool
from gevent.queue import Queue
from framework.common import constant
from collections import OrderedDict
from worker_pool import WorkerPool
from workers import debug_worker


__all__ = ["Chain"]


def running_status_udpate(func):
    def wrap(*args, **kwargs):
        self = args[0]
        self.status = constant.RunningStatus.running
        ret = func(*args, **kwargs)
        self.status = constant.RunningStatus.not_running
        return ret

    return wrap


class Chain(object):
    """
    使用队列实现的并发可控工作流
    """
    DEFAULT_POOL_SIZE = 1
    DEFAULT_INTERVAL = None
    DEFAULT_QUE_SIZE = 10

    def __init__(self, **kwargs):
        self.chains = []
        self.stat = {
            'total_usage': None,
            'nodes': OrderedDict()
        }
        self.pools = []
        self.status = constant.RunningStatus.not_running

        # 如果数据量大的话，必须限制队列的大小，否则会造成内存消耗过大
        if kwargs.has_key('que_size'):
            self.default_que_size = kwargs['que_size']
        else:
            self.default_que_size = self.DEFAULT_QUE_SIZE

    def call(self, func, args=[], pool_size=DEFAULT_POOL_SIZE, interval=DEFAULT_INTERVAL, **kwargs):
        """
        向当前执行流添加新的节点, 相当于注册
        :param func:
        :param args:
        :param pool_size: worker数量，针对单个方法的并发控制
        :param interval: 执行间隔
        :return:
        """
        # 当第一个分发节点受限时, 内存占用量很大？
        if kwargs.has_key('que_size'):
            que_size = kwargs['que_size']
        else:
            que_size = self.default_que_size

        exec_info = {
            'func': func,
            'args': args,
            'pool_size': pool_size,
            'interval': interval,
            'que_size': que_size,
        }

        self.chains.append(exec_info)
        return self

    def batch_call(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    @running_status_udpate
    def execute(self, debug=False, debug_interval=1, dump_memory_usage={}):
        """

        :param debug:
        :param debug_interval:
        :param dump_memory_usage:
            dump_heap: 打印堆
            dump_growth: 打印使用最多内存的对象 及其增长速度
            dump_ctx_list: 打印所有ctx 对象占用内存的大小
        :return:
        """
        chains_len = len(self.chains)
        queues = []
        for ind in range(chains_len):
            exec_info = self.chains[ind]
            que = Queue(exec_info['que_size'])

            self.chains[ind]['queue'] = que
            queues.append(que)

        pools = self.pools
        for ind in range(chains_len):
            exec_info = self.chains[ind]

            func = exec_info['func']
            args = exec_info['args']
            pool_size = exec_info['pool_size']
            interval = exec_info['interval']

            from_que = None
            if ind != 0:
                from_que = self.chains[ind]['queue']

            to_que = None
            if ind != (chains_len-1):
                to_que = self.chains[ind+1]['queue']

            # print from_que, to_que

            p = WorkerPool(from_que, to_que, pool_size, func, args, queues, pools, ind, interval)

            pools.append(p)

        # print len(pools)
        started_at = time.time()

        # for p in pools:
        #     p.join()
        pool_mgr = Pool(len(pools)+1)
        for p in pools:
            pool_mgr.spawn(p.join)

        if debug is True:
            pool_mgr.spawn(debug_worker, pools, debug_interval, dump_memory_usage)

        pool_mgr.join()

        time_usage = time.time() - started_at

        self.stat['failed'] = 0
        self.stat['total'] = 0
        for p in pools:
            node_name = '.'.join([str(p.func.im_class), p.func.__name__])
            self.stat['nodes'][node_name] = {
                'failed': p.failed,
                'total': p.total,
                'task_exec': p.task_exec,
                'time_usage': p.total_time_usage,
            }
            self.stat['failed'] += p.failed
            self.stat['total'] += p.total

        self.stat['total_usage'] = time_usage


def release_list(a):
   del a[:]
   del a


def main():
    def test1():
        print 'go'
        gevent.sleep(1)
        return range(11, 20)

    def test2(res1):
        print res1
        gevent.sleep(1)
        return range(10)
        # return 'b'

    def test3(res2):
        print res2
        return 'c'

    chain = Chain()

    chain.call(
        test1, pool_size=1
    ).call(
        test2, pool_size=1
    ).call(
        test3
    ).execute()






