#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import os
import sys
from smtplib import SMTP, SMTP_SSL, SMTPAuthenticationError, SMTPConnectError, SMTPSenderRefused
import configparser
import socket
import random
import string

import re
import platform
import shlex

jms_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(jms_dir)


def bash(cmd):
    """
    run a bash shell command
    执行bash命令
    """
    return shlex.os.system(cmd)


def valid_ip(ip):
    if ('255' in ip) or (ip == "0.0.0.0"):
        return False
    else:
        return True


def color_print(msg, color='red', exits=False):
    """
    Print colorful string.
    颜色打印字符或者退出
    """
    color_msg = {'blue': '\033[1;36m%s\033[0m',
                 'green': '\033[1;32m%s\033[0m',
                 'yellow': '\033[1;33m%s\033[0m',
                 'red': '\033[1;31m%s\033[0m',
                 'title': '\033[30;42m%s\033[0m',
                 'info': '\033[32m%s\033[0m'}
    msg = color_msg.get(color, 'red') % msg
    print(msg)
    if exits:
        time.sleep(2)
        sys.exit()
    return msg

class PreSetup(object):
    def __init__(self,*args,**kwargs):
        self.host = ''

if __name__ == '__main__':
    pre_setup = PreSetup()
    custom_mysql = input("是否默认安装本程序(y/n):")
    if custom_mysql != 'n':
        pre_setup.start()
    else:
        host = input('请输入MySQL服务器地址:')
