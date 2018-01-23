#!/usr/bin/python
# -*- coding:utf-8 -*-

import socketserver,json,subprocess,paramiko,os,time
from host_monitor.admin_base import site
# from host_monitor.views import admin_func

def sock_server(obj_id):
    print('启动socket server')
    server = socketserver.ThreadingTCPServer(('0.0.0.0',51461),MyServer)

    server.serve_forever(obj_id)
class MyServer(socketserver.BaseRequestHandler):

    def handle(self):
        admin_class = self.sock_to_db()
        print('admin_class',admin_class)
        conn = self.request
        Flag = True
        while Flag:
            data = conn.recv(20480)
            if not data:
                continue
            print('data', json.loads(data))

            data = json.loads(data)
            # self.sock_to_db(data)
            print("admin_class", admin_class)
            print("获取的queryset")
            print("执行插入操作")
            host_id = self.insert_data(data, admin_class)

            self.update_data(data, admin_class, host_id)


    def sock_to_db(self):
        '''save data for socketserver to database'''
        print('接收到数据，获取数据库信息')
        for app_name in site.registered_admins:
            admin_class = site.registered_admins[app_name]
            print('admin_class',admin_class)
            return admin_class



    def selete_data(self,data,obj):
        ''' 查询主机IP是否在host表 '''
        print("查询操作")
        host_ip = data.get('ip_address')
        for obj_ip in obj.model.objects.values("ip_address").distinct():
            if host_ip == obj_ip.get('ip_address'):
                host_id = obj.model.objects.values('id').get(ip_address=host_ip).get('id')
                return host_id  #代表数据库中存在此主机,返回ID
        return False

    def insert_data(self,data,admin_class):
        print("执行插入操作")
        obj = admin_class.get('host')
        host_id = self.selete_data(data,obj)

        if host_id :

            return host_id
        else:
            print('数据库中没有此主机,开始插入主机数据')
            obj.model.objects.create(hostname=data.get("hostname"),
                                     ip_address=data.get("ip_address"),)
            print('主机数据插入完毕，获取主机ID')
            if True:
                host_id = obj.model.objects.values('id').get(ip_address=data.get("ip_address")).get('id')
                print('主机ID获取完毕')
                return host_id


    def update_data(self,data,admin_class,host_id):
        print("执行update操作")
        obj = admin_class.get('monitor')
        obj.model.objects.create(hostname_id=host_id,
                                 cpu_use=data.get('cpu_use'),
                                 cpu_total=data.get('cpu_count'),
                                 ram_use=data.get('ram_use'),
                                 ram_total=data.get('ram_total'),
                                 disk_use=data.get('disk_use'),
                                 disk_total=data.get('disk_total'),
                                 host_input=data.get('host_input'),
                                 host_output=data.get('host_output'))
        print('监控数据更新完成')
        time.sleep(2)
        print('更新Pod数据')
        obj = admin_class.get('pod')
        for index,info in enumerate(data.get("c_info")):
            info = data.get('c_info')['%s' %index]
            for ip in info.get("NetworkSettings").get("Ports"):
                for host_ip in info.get("NetworkSettings").get("Ports").get(ip):
                    start_data = self.data_func(info)
                    obj.model.objects.create(container_id=info.get('Id'),
                                             name=info.get("Name")[1:],
                                             ipaddress=info.get("NetworkSettings").get('IPAddress'),
                                             gateway=info.get("NetworkSettings").get("Gateway"),
                                             hostip=host_ip.get("HostIp"),
                                             hostport=host_ip.get("HostPort"),
                                             image=info.get("Config").get("Image"),
                                             image_id=info.get("Config").get("Hostname"),
                                             pod_status=info.get('State').get("Status"),
                                             ports=host_ip.get("HostPort"),
                                             start_data= start_data,
                                             hostname = host_id,
                                             )
    def data_func(self,info):
        t = info.get('State').get('StartedAt')
        start_data = t.split('T')[0] + " " + t.split('T')[1].split('.')[0]
        return start_data

start_socket = sock_server(1)
print('启动socket',start_socket)