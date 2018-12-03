#coding:utf-8
import gevent


def dump_mem_usage(**kwargs):
    if kwargs.get('dump_heap'):
        try:
            from guppy import hpy
        except ImportError:
            return
        hxx = hpy()
        heap = hxx.heap()
        print(heap)

    if kwargs.get('dump_growth'):
        try:
            import objgraph
        except ImportError:
            return
        objgraph.show_growth()

    if kwargs.get('dump_ctx_list'):
        try:
            from pympler.asizeof import asizeof
        except:
            return

        global CTX_LIST
        print len(CTX_LIST)
        print asizeof(CTX_LIST)/1000/1000, 'MB'


def debug_worker(pools, interval=1, dump_memory_usage={}):
    pool_count = len(pools)
    while 1:
        all_done = 0
        print '*' * 80
        line1 = []
        line2 = []
        line3 = []
        for ind in range(pool_count):
            p = pools[ind]

            if p.is_task_done is True:
                all_done += 1

            line3.append(''.join(('(', str(ind), ')', p.func.__name__, '(', str(p.total), ')')))
            line1.append(str(ind) + '-' + str(p.actives))
            line2.append(str(ind) + '-' + str(p.from_que is not None and p.from_que.qsize() or 0))

        print 'Workers       :', '  '.join(line3)
        print 'Active Workers:', '    '.join(line1)
        print 'Worker Queue  :', '    '.join(line2)

        if dump_memory_usage:
            dump_mem_usage(**dump_memory_usage)

        if all_done == pool_count:
            break
        gevent.sleep(interval)