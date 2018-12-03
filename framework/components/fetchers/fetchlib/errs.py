#coding:utf-8


class CommonProxyErr(Exception):
    pass


class CommonSSLErr(Exception):
    pass


class RetryExec(Exception):
    pass


class FailedErr(Exception):
    pass


class SwitchNodeErr(Exception):
    pass