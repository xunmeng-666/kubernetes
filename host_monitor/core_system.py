import socketserver,json,subprocess,paramiko,os,time
from host_monitor import models


def conn_action(func,obj_id):
    '''
    上传文件 + 执行初始化程序 + redis转储
    :param func:
    :return:
    '''

    local_dir = os.getcwd() + '/monitor_node/'
    remote_dir = '/tmp/monitor_node/'
    upfile_client = upfile(func,local_dir, remote_dir)
    print('upfile_client-status',upfile_client)
    if upfile_client != 1:
        print('文件上传成功')
        print('开始SSH连接')
        print('host-ip:',type(func.ip_address))
        conn_client = conn_command(func)
        print('conn_client', conn_client)
        print('本地redis获取数据')
        if conn_client:
            print('SSH连接成功')
            # redis_to_db(obj_id)
            return True
        else:
            print('ssh 连接失败')
        return conn_client
    else:
        print('文件上传失败')
        return 1

class Conn_paramiko(object):
    def __init__(self,func):

        self.hostname = func.ip_address
        self.port = func.port
        self.username = func.username
        self.password = func.password
        self.key = func.host_key
        self.start_conn()
        self.remotefile = "/var/lib/"
        self.loadfile = None
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def start_conn(self):
        print('key',self.key)

        if not self.key:
            print('没有检测到key，使用密码连接主机')
            conn_status = self.pwd_conn()
            return conn_status
        else:
            print("使用key连接主机")
            conn_status = self.key_conn()
            return conn_status
    def pwd_conn(self):
        try:
            self.ssh.connect(hostname=self.hostname,port=self.port,username=self.username,password=self.password,timeout=10)

            print("连接成功")
            return True
        except Exception :
            print('连接失败')
            return False
    def key_conn(self):
        try:
            self.ssh.connect(hostname=self.hostname,port=self.port,username=self.username,key_filename=self.key,timeout=10)
            return True
        except Exception :
            return False

    def put_file(self):
        pass
    def check_file(self):
        pass

# def conn_paramiko(func):
#     print('func--',func.ip_address)
#     ssh = paramiko.SSHClient()
#     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     try:
#         ssh.connect(hostname=func.ip_address, port=22, username=func.username, password=func.password, timeout=10)
#     # print('ssh_status',ssh_status)
#
#
#         return True
#     except Exception as e:

        # return False

def conn_command(func):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=func.ip_address, port=22, username=func.username, password=func.password, timeout=10)
    print('开始执行初始化脚本')
    stdin,stdout,stderr =  ssh.exec_command('sh /tmp/monitor_node/install.sh')
    print('初始化脚本执行完毕，返回正确状态码',stdout)
    # if stderr:
    #     return False
    return True




def upfile(func,local_dir,remote_dir):
    print('local_dir',local_dir)
    print('remote_dir',remote_dir)
    print('ip-',func.ip_address)
    print('ip-user',func.username)
    print('ip-pwd',func.password)
    print('os-walk',os.walk(local_dir))
    try:
        t=paramiko.Transport(func.ip_address,func.port)
        t.connect(username=func.username,password=func.password)
        print('t------',t)
        sftp=paramiko.SFTPClient.from_transport(t)
        print('sftp---',sftp)
        for root,dirs,files in os.walk(local_dir):
            for filespath in files:
                print('上传的是文件')
                local_file = os.path.join(root,filespath)
                a = local_file.replace(local_dir,'')
                remote_file = os.path.join(remote_dir,a)
                try:
                    sftp.put(local_file,remote_file)
                except Exception as e:
                    sftp.mkdir(os.path.split(remote_file)[0])
                    sftp.put(local_file,remote_file)
                print ("upload %s to remote %s" % (local_file,remote_file))
            for name in dirs:
                print('上传的是目录')
                local_path = os.path.join(root,name)
                a = local_path.replace(local_dir,'')
                print('aa',a)
                remote_path = os.path.join(remote_dir,a)
                print('remote_path---',remote_path)
                try:
                    sftp.mkdir(remote_path)
                    print("mkdir path %s" % remote_path)
                except Exception as e:
                    print(e)
        t.close()
        return 0
    except Exception as e:
        print(e)
        return 1


# def conn_r_redis():
#     ''' redis 转储'''
#     # pool = redis.ConnectionPool(host='192.168.31.116', port=6379, max_connections=10)
#     pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
#     print('已连接到redis')
#     conn = redis.Redis(connection_pool=pool)
#     pub = conn.pubsub()
#     print('订阅频道')
#     pub.subscribe('kubernetes')
#     while True:
#         print('循环中...')
#         data = pub.parse_response()[2]
#         print('1',data)
#         if data != 1:
#             if not data:
#                 print('data 为空')
#                 return data
#             else:
#                 print('data',data)
#                 host_val = json.loads(data)
#                 print('redis-data', host_val)
#
#                 return host_val
#
#         else:
#             print('data',data)
#             pass

