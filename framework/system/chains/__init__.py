#coding:utf-8
import types
from functools import wraps

from chains import *
from worker_pool import *


def set_res(_ctx, i):
    setattr(_ctx, 'res', i)
    return _ctx


def init_ctx():
    global CTX_COUNT
    ctx = Ctx__()
    CTX_COUNT += 1
    return ctx


def set_ctx(_ctx, ctx_like):
    for k, v in ctx_like.items():
        setattr(_ctx, k, v)
    return _ctx


def wrap_ctx(args=None):
    def wrap_ctx_(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            ctx_before = None
            if len(args) > 1:
                ctx_before = args[1]

            ret = func(*args, **kwargs)

            if isinstance(ret, (list, tuple, types.GeneratorType)):
                reses = []
                for i in ret:
                    _ctx = init_ctx()

                    if isinstance(i, Ctx):
                        _ctx = set_ctx(_ctx, i)
                    else:
                        _ctx = set_res(_ctx, i)

                    _ctx.ctx = ctx_before
                    reses.append(_ctx)

                return reses

            else:
                _ctx = ctx_before
                if _ctx is None:
                    _ctx = init_ctx()

                if isinstance(ret, Ctx):
                    _ctx = set_ctx(_ctx, ret)
                else:
                    # import pdb;pdb.set_trace()
                    _ctx = set_res(_ctx, ret)

                return _ctx

        return wrap
    return wrap_ctx_


def for_all_methods(decorator, excludes=[]):
    def decorate(cls):
        for attr in cls.__dict__:   # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                if not attr.startswith('__') and attr not in excludes:
                    setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate


def wrap_all_method_ctx(excludes=[]):
    return for_all_methods(wrap_ctx(), excludes=excludes)


