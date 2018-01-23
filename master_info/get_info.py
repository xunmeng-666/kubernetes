#!/usr/bin/python
# -*- coding:utf-8 -*-


from kubernetes import client, config
from master_info.save_to_db import Save_Master_Data

class Get_info(object):

    def __init__(self,conf,client_func):
        self.config = conf
        self.client_func = client_func

    def get_info(self):
        node_status = {}
        ret = self.client_func.list_node()
        for index,func_info in enumerate(ret.items):
            role = func_info.metadata.labels.get("node-role.kubernetes.io/master")
            for func_status in func_info.status.conditions:
                if "True" in func_status.status:

                    if role == 'true':
                        node_status.update({index:{'name': func_info.spec.external_id,
                                            'status': "Ready",
                                            'ROLES':'master',
                                            'version': func_info.status.node_info.kubelet_version}})
                    else:
                        node_status.update({index:{'name': func_info.spec.external_id,
                                            'status': "Ready",
                                            'ROLES': 'node',
                                            'version': func_info.status.node_info.kubelet_version}})
                else:
                    if role == 'true':
                        node_status.update({index:{'name': func_info.spec.external_id,
                                            'status': "NotReady",
                                            'ROLES':'master',
                                            'version': func_info.status.node_info.kubelet_version}})
                    else:
                        node_status.update({index:{'name': func_info.spec.external_id,
                                            'status': "NotReady",
                                            'ROLES': 'node',
                                            'version': func_info.status.node_info.kubelet_version}})
        Save_Master_Data().update_data(node_status)


if __name__=="__main__":
    conf = config.load_kube_config()
    client_func = client.CoreV1Api()
    Get_info(conf,client_func)



