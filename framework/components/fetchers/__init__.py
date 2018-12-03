#coding:utf-8
import logging
logger = logging.getLogger(__name__)

from fetchlib import base
from fetchlib import base as fetch_main
from framework.common import constant
from framework.libs import utils
from fetchlib import errs


def fetcher(url, kwargs):
    res = fetch_main.fetcher_main(url, kwargs)
    return utils.Msg(code=constant.Code.success, data=res)





















