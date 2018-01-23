#!/usr/bin/python
# -*- coding:utf-8 -*-

from host_monitor.admin_base import site

class Save_Master_Data(object):

    def func_db(self):

        for app_name in site.registered_admins:
            if app_name in site.registered_admins:
                admin_class = site.registered_admins[app_name]
                return admin_class

    def selete_ns_id(self,info,admin_class):
        '''查询namespace 并返回ID'''

        obj = admin_class.get('namespaces')
        for ns in obj.model.objects.values("name").distinct():
            if info.get("namespace") in ns.get("name"):
                print('找到namespace %s，返回此namespace ID' %info.get("namespace"))
                ns_id = obj.model.objects.values('id').get(name=info.get('namespace')).get('id')
                return ns_id
            else:
                print('数据库中没有此namespace:%s' %info.get("namespace"))
                print('开始保存数据')
                obj.model.objects.create(name=info.get("namespace"))
                print('NameSpace:%s 保存成功' %info.get("namespace") )
                ns_id = obj.model.objects.values('id').get(name=info.get('namespace')).get('id')
                return ns_id

    def selete_host_id(self,info,admin_class):
        obj = admin_class.get("host")
        for host in obj.model.objects.values("ip_address").distinct():
            if info.get("node_ip") in host.get("ip_address"):
                print('找到Node：%s的记录' %host.get("ip_address"))
                host_id = obj.model.objects.values('id').get(ip_address=info.get('ip_address')).get('id')
                print('获取到主机ID：%s' %host_id)
                return host_id

    def selete_pod_id(self,info,admin_class):
        obj = admin_class.get("pod")
        for host in obj.model.objects.values("pod_ip").distinct():
            if info.get("pod_ip") in host.get("pod_ip"):
                print('找到Pod：%s的记录' %host.get("pod_ip"))
                host_id = obj.model.objects.values('id').get(ip_address=info.get('pod_ip')).get('id')
                print('获取到PodID：%s' %host_id)
                return host_id

    def update_data(self,info):
        '''更新master 数据'''
        for key in info:
            info = info[key]

        admin_class = self.func_db()
        ns_id = self.selete_ns_id(info,admin_class)
        host_id = self.selete_host_id(info,admin_class)
        pod_id = self.selete_pod_id(info,admin_class)
        admin_class=admin_class.get('master')
        print("开始更新数据")
        admin_class.model.objects.create(ns_id=ns_id,
                                         node_ip=host_id,
                                         pod_ip=pod_id,
                                         start_time=info.get("start_time").split("+")[0],
                                         )

        print("Master信息更新成功")