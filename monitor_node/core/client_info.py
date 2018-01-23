#!/usr/bin/env python
from monitor_node.conf import config
import psutil,time,redis,json
import socket,docker

# from host_info.core_system import conn_w_redis
class Host_info(object):
    count = 1024 * 1024 * 1024
    def __init__(self,):
        # host_total = self.host_total()
        pass
    def host_total(self):
        data = {}
        data.update(self.Hostname())
        data.update(self.Host_CPU())
        data.update(self.Host_Ram())
        data.update(self.Host_disk())
        data.update(self.Host_input())
        data.update(self.Host_output())
        data.update(self.Now_time())
        data.update(self.get_container_info())

        return data
    def Hostname(self):
        ip_address = psutil.net_if_addrs().get(config.NETWORK_NAME)
        # return ip_address[0].address
        return {'ip_address':ip_address[0].address}

    def Host_CPU(self):
        # CPU 逻辑核数+物理核数

        use_rate = psutil.cpu_times_percent()
        cpu_use = str(int(use_rate.user + use_rate.system))+"%"
        cpu_count = psutil.cpu_count(logical=False)
        return {'cpu_use':cpu_use,'cpu_count':cpu_count}
        # return cpu_use

    def Host_disk(self):
        disk = psutil.disk_usage('/')  # 获取硬盘使用情况
        # disk_use = int(disk_zone.used / disk_zone.total * 100)
        disk_use = str(int(disk.used / disk.total * 100))+'%'
        disk_total = str(int(disk.total / 1024/1024/1024))+"G"
        # return disk_use
        return {'disk_use':disk_use,'disk_total':disk_total}

    def Host_Ram(self):
        '''内存统计'''
        mem = psutil.virtual_memory()
        ram_use = str(int((mem.used / mem.total)*100)) +"%"
        ram_total = str(int(mem.total / 1024 / 1024 /1024))+"G"
        # ram_use = int(mem.used / mem.total * 100)
        # return ram_use
        return {'ram_use':ram_use,'ram_total':ram_total}

    def Now_time(self):
        '''返回当前时间，流量图调用'''
        sys_run_time = time.strftime("%H:%M", time.localtime())
        # return sys_run_time
        return {'sys_run_time':sys_run_time}

    def Host_input(self):
        '''网卡接收流量'''
        old_recv = psutil.net_io_counters(pernic=True).get(config.NETWORK_NAME).bytes_recv
        time.sleep(1)
        new_recv = psutil.net_io_counters(pernic=True).get(config.NETWORK_NAME).bytes_recv
        input_recv = (new_recv - old_recv) / 1024
        host_input = str(int(input_recv) / 1024)
        if input_recv > 1024:
            host_input = str(int(input_recv) / 1024) + "M"
        else:
            host_input = str(int(input_recv)) + "K"
        # return host_input
        return {'host_input': host_input}

    def Host_output(self):
        '''发送流量'''
        old_info = psutil.net_io_counters(pernic=True).get(config.NETWORK_NAME).bytes_sent
        time.sleep(1)
        new_info = psutil.net_io_counters(pernic=True).get(config.NETWORK_NAME).bytes_sent
        out_sent = (new_info - old_info) / 1024
        host_output = str(int(out_sent) / 1024)
        if out_sent > 1024:
            host_output = str(int(out_sent) / 1024) + 'M'
        else:
            host_output = str(int(out_sent)) + 'K'
        # return host_output
        return {'host_output': host_output}

    def get_container_info(self):
        client = docker.DockerClient(base_url="unix://" + config.Docker_sock, version="auto", timeout=config.TIME_OUT)
        c_obj = client.containers.list()
        c_info = {}
        for index, c_obj in enumerate(c_obj):
            c_info["%s" % index] = c_obj.attrs
        return {"c_info":c_info}


def func_total():
    while True:
        try:

            client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client.connect((config.SERVER_IP,config.SERVER_PORT))
        except ConnectionRefusedError:
            print('2')
            time.sleep(10)
            continue
        print('连接socket server')
        while True:
            time.sleep(10)
            print('获取数据')
            total_data = Host_info().host_total()
            print('total_data',total_data)
            client.sendall(json.dumps(total_data).encode("utf-8"))


a = func_total()
print(a)