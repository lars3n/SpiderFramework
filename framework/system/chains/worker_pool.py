#coding:utf-8
import types
import logging
logger = logging.getLogger(__name__)
import sys
import datetime
import traceback
import time
from gevent.pool import Pool
import gevent

__all__ = ['StopExec', 'Ctx', 'ListCtx', 'Ctx__', 'CTX_COUNT', 'GoTo']

CTX_COUNT = 0


class ListCtx(list):
    pass


class ArgObj(tuple):
    pass


class Ctx__(object):

    def __call__(self, loop=0):
        ctx_obj = self
        for i in range(loop):
            ctx_obj = getattr(ctx_obj, 'ctx')
        return ctx_obj


class Ctx(dict):
    pass


class StopExec(Exception):
    pass


class GoTo(object):
    def __init__(self, func, ctx):
        self.tgt_func = func
        self.ctx = ctx


class WorkerPool(object):
    """
    每个工作流节点的执行线程池
    """

    def __init__(self, from_que, to_que, pool_size, func, args, queues, pools, index, interval):
        self.func = func
        self.args = args
        self.pool_size = pool_size

        self.pool = Pool(pool_size)

        self.from_que = from_que
        self.to_que = to_que

        self.queues = queues
        self.pools = pools

        self.is_task_done = False
        self.index = index
        self.last_exec_time = 0
        self.interval = interval

        self.failed = 0
        self.total = 0
        self.task_exec = {}
        self.total_time_usage = 0

        self.actives = 0

    def execute(self, args):
        self.total += 1
        self.actives += 1

        continue_ = False
        res = None
        try:
            # 控制执行频率
            if self.interval is not None:
                is_lt_interval = (time.time() - self.last_exec_time) < self.interval
                if is_lt_interval:
                    while (time.time() - self.last_exec_time) < self.interval:
                        gevent.sleep(0.1)
                else:
                    # logger.warn('Adding worker...')
                    pass

                self.last_exec_time = time.time()

            _started_at = time.time()

            res = self.func(*args)

            _time_usage = time.time() - _started_at
            self.total_time_usage += _time_usage

        except StopExec, e:
            continue_ = True

        except Exception, e:
            err = traceback.format_exc()
            logger.error(err)
            self.failed += 1

            e_str = str(e)
            if e_str not in self.task_exec:  # 节省内存
                _args = None
                # if self.log_ctx is True:
                #     _args = args

                self.task_exec[e_str] = {
                    'args': _args,  # 可能会存在内存泄漏点
                    'err': err,
                    'e': e,
                    # 'local_vars': utils.format_exc_vars()
                    'local_vars': None,
                    'time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            continue_ = True

        self.actives -= 1
        return continue_, res

    def put(self, que, res):
        def _put(que, res):
            while 1:
                try:
                    que.put_nowait(res)
                    break
                except Exception, e:
                    gevent.sleep(0.01)

        if isinstance(res, (list, tuple, types.GeneratorType)):
            for i in res:
                # que.put(i)
                _put(que, i)
        else:
            # que.put(res)
            _put(que, res)

    def worker(self):
        is_worker_done = False
        while 1:
            if is_worker_done is True:
                break

            if self.from_que is not None:
                raw_data = None

                while 1:
                    pre_pool = self.pools[self.index - 1]
                    if pre_pool.is_task_done is True and self.from_que.empty():     # 当前一节点结束且当前任务队列为空时
                        is_worker_done = True
                        break

                    # 非阻塞式获取，防止gevent 永久堵塞
                    try:
                        raw_data = self.from_que.get(block=False)
                        break
                    except Exception, e:
                        gevent.sleep(0.1)

                if is_worker_done is True:
                    break

                args = ArgObj([raw_data] + self.args)
            else:
                args = ArgObj()
                is_worker_done = True

            continue_, res = self.execute(args)

            if continue_:
                continue

            if isinstance(res, GoTo):
                for p in self.pools:
                    if p.func == res.tgt_func:
                        _que = p.from_que
                        break

                self.put(_que, res.ctx)

            else:
                # 新增任务到下一个节点
                if self.to_que is not None:
                    self.put(self.to_que, res)

    def join(self):
        for i in range(self.pool_size):
            gt = self.pool.spawn(self.worker)

        self.pool.join()
        self.is_task_done = True