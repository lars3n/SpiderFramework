# coding:utf-8
"""
python command/run.py 脚本路径(相对路径)

-i:(可选), 持续运行，并以此参数值为运行间隔
--loglv:(可选)，指定打印的日志级别，如" --loglv=info"
--configs: (可选),配置文件目录, 默认为代码目录下configs 文件夹
"""

import sys
import os
fw_path = os.path.dirname(sys.path[0])
sys.path.append(fw_path)

from gevent import monkey
monkey.patch_all()

from framework.libs import log
import logging

import importlib, imp
import click
import time
import datetime


LENIENT_CONTEXT = dict(ignore_unknown_options=True, allow_extra_args=True)


def import_by_mod(path):
    module = path
    module = module.replace('/', '.').replace('\\', '.').rstrip('py').rstrip('.')
    pack = importlib.import_module(module, __package__)
    return pack


@click.command(context_settings=LENIENT_CONTEXT)
@click.argument('path')
@click.argument('null', nargs=-1)
@click.option('-i', '--interval', default=None, type=int)
@click.option('--debug', default=0, type=int)
@click.option('--loglv', default='info')
@click.option('--config', default='configs')
# @click.pass_context
def parse(path, null, interval, debug, loglv, config):
    logging = log.initLog(loglv)
    logger = logging.getLogger(__name__)

    if interval is not None:
        while 1:
            last_exec = time.time()
            pack = import_by_mod(path)
            pack.main()

            time_usage = time.time() - last_exec
            time_rest = interval - time_usage

            next_exec_stamp = time.time() + time_rest
            next_exec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_exec_stamp))
            if time_rest > 0:
                timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                logger.info(u'更新于:%s, 用时:%f,  挂起%f 秒, 下一次执行时间:%s' % (timestr, time_usage, time_rest, next_exec))
                time.sleep(time_rest)

            print '*'*70

    else:
        pack = import_by_mod(path)
        pack.main()


if __name__ == '__main__':
    parse()

