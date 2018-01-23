#!/usr/bin/env python

# REDIS 服务器配置
REDIS_IP = '192.168.1.108'
REDIS_PORT = 6379
REDIS_PASS = ''
REDIS_TIMEOUT = 10  #REDIS 过期时间

#连接信息配置

CONN_TIMEOUT = 300       #连接超时时间
RE_CONN_TIME = 5    #重新连接时间
DATA_TO_REDIS_TIME = 3   #客户端数据发送至redis时间

#网卡设置

NETWORK_NAME='en0'

SERVER_IP = '127.0.0.1'
SERVER_PORT = 51461
#发送数据延迟设置

TIME_OUT = 10

Docker_sock = "/private/var/run/docker.sock"