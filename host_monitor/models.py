import os
os.environ.update({"DJANGO_SETTINGS_MODULE": "k8s_monitor.settings"})

from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser,PermissionsMixin)


# Create your models here.

class IDC(models.Model):
    name = models.CharField('机房名字',max_length=64,unique=True)
    address = models.CharField('机房地址',max_length=128,blank=True,unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "机房信息"
        verbose_name_plural = "机房信息"

class Host(models.Model):
    """主机表"""

    hostname = models.CharField("主机名",max_length=64,blank=True,unique=True)
    ip_address = models.GenericIPAddressField("IP地址", unique=True)
    idc = models.ForeignKey("IDC",verbose_name='机房')
    username = models.CharField('系统用户',max_length=64,default='root')
    host_key = models.CharField("系统秘钥",max_length=255,blank=True,null=True)
    password = models.CharField("系统密码",max_length=128,blank=True,null=True)
    port = models.IntegerField("SSH端口",default=22)
    pod_count = models.IntegerField("容器数量",blank=True,null=True)
    date = models.DateField(auto_now_add=True)
    host_active = models.CharField(verbose_name='连接',default='未连接',max_length=12,blank=True,null=True)
    host_group = models.ForeignKey('HostGroup',to_field='group_name',verbose_name='主机组',blank=True,null=True)

    def __str__(self):
        return "%s %s %s %s " %(self.hostname,self.ip_address,self.host_group,self.idc)
    class Meta:
        unique_together = ("password","host_key")
        verbose_name = '主机信息表'
        verbose_name_plural = '主机信息表'


class NameSpaces(models.Model):
    '''命名空间'''
    name = models.CharField("项目名称", max_length=32, unique=True)
    remark = models.CharField(verbose_name="备注", max_length=128, blank=True, null=True)
    class Meta:
        verbose_name = "项目管理"
        verbose_name_plural = "项目管理"

class Pod(models.Model):


    name = models.CharField('Pod名字',max_length=256)
    pod_ip = models.GenericIPAddressField(verbose_name='PodIP',unique=True)
    gateway = models.GenericIPAddressField(verbose_name='网关')
    host=models.GenericIPAddressField(verbose_name='对外IP')
    hostport = models.IntegerField("对外端口号")
    namespaces = models.ForeignKey("NameSpaces", )
    image = models.CharField("原生镜像", max_length=128, blank=True, unique=True)
    image_id = models.CharField("镜像名", max_length=128, blank=True, unique=True)
    pod_status = models.CharField("状态", max_length=128, blank=True, unique=True)
    ports = models.CharField("端口", max_length=128, blank=True, unique=True)
    start_data = models.DateTimeField("启动时间", auto_now_add=True)
    host = models.ForeignKey("Host")
    container_id = models.CharField("ID", max_length=256)

    class Meta:
        verbose_name = '节点信息表'
        verbose_name_plural = '节点信息表'

    def __str__(self):
        return "%s-%s" %(self.container_id,self.image_id)

class Master(models.Model):
    '''集群表'''

    host = models.ForeignKey("Host",verbose_name='主机')
    status = models.CharField("状态",max_length=32,blank=True,null=True)
    roles_method_choices = ((0,'master'),
                            (1,'node'))
    roles = models.SmallIntegerField("角色",choices=roles_method_choices,unique=True)
    version = models.CharField("版本",max_length=32,blank=True,null=True)
    namespaces = models.ForeignKey("NameSpaces",verbose_name='项目名称')
    class Meta:
        verbose_name = '集群信息表'
        verbose_name_plural = '集群信息表'

    def __str__(self):
        return "%s-%s-%s-%s" %(self.host,self.status,self.roles,self.version)
class HostGroup(models.Model):
    """主机组"""
    group_name = models.CharField(verbose_name='主机组',max_length=64,unique=True)
    host_count = models.IntegerField('主机数量',blank=True,null=True)
    remark = models.CharField(verbose_name="备注",max_length=128, blank=True,null=True)

    def __str__(self):
        return "%s-%s-%s" %(self.group_name,self.host_count,self.remark)
    class Meta:
        verbose_name = '主机组'
        verbose_name_plural = '主机组'

class SystemUser(models.Model):
    """主机用户"""
    username = models.CharField('系统用户',max_length=64)
    auth_type_choices = ((0,'ssh-password'),(1,'ssh-key'))
    auth_type = models.SmallIntegerField(choices=auth_type_choices,default=0)
    password = models.CharField(max_length=128,blank=True,null=True,)

    class Meta:
        unique_together  = ('username','password')
        verbose_name = '系统用户'
        verbose_name_plural = '系统用户'

    def __str__(self):
        return "%s-%s-%s" %(self.username,self.get_auth_type_display(),self.password)

class AuditLog(models.Model):
    """审计日志"""
    idc = models.ForeignKey("IDC")
    node = models.ForeignKey("Host")
    image_name = models.ForeignKey("Pod")
    cmd = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return "%s" %(self.cmd)

class Monitor(models.Model):
    hostname = models.ForeignKey(Host ,verbose_name='主机',on_delete=models.CASCADE)
    cpu_use = models.CharField(max_length=12,verbose_name='CPU使用率')
    cpu_total = models.CharField(max_length=12,verbose_name="CPU总数")
    ram_use = models.CharField(max_length=12,verbose_name="内存使用率")
    ram_total = models.CharField(max_length=12,verbose_name="内存总数")
    disk_use = models.CharField(max_length=12,verbose_name='磁盘使用率')
    disk_total=models.CharField(max_length=12,verbose_name="磁盘总数")
    host_input = models.CharField(max_length=12,verbose_name="下载流量")
    host_output = models.CharField(max_length=12,verbose_name="上传流量")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together = ("hostname",'cpu_use','cpu_total','ram_use','ram_total','disk_use','disk_total','host_input','host_output')
        verbose_name = '主机监控'
        verbose_name_plural = '主机监控'



class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user



class Account(AbstractBaseUser,PermissionsMixin):
    '''平台用户'''
    email = models.EmailField(
        verbose_name='邮件地址',
        max_length=255,
        unique=True,
    )
    name = models.CharField('姓名',max_length=32)
    is_active = models.BooleanField('激活',default=True)
    is_staff = models.BooleanField(
        'staff status',
        default=True,
        help_text='Designates whether the user can log into this admin site.',
    )

    # bind_host_users =  models.ManyToManyField("BindHostUser",blank=True)
    # host_groups = models.ManyToManyField("HostGroup",blank=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email
    class Meta:
        permissions = (
            ('crm_table_index','可以查看所有的项目'),
            ('crm_table_list','可以查看每张表里所有的数据'),
            ('crm_table_list_view','可以访问表里每条数据的修改页'),
            ('crm_table_list_change','可以对表里的每条数据进行修改'),
        )

        verbose_name = '用户列表'
        verbose_name_plural = '用户管理'




