from django.contrib import admin
from django import forms
from host_monitor.admin_base import site
# Register your models here.
from host_monitor import models
from host_monitor.admin_base import site,BaseAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField




class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = models.Account
        fields = ('email', 'name','is_active','is_superuser')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.Account
        fields = ('email', 'password', 'name', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class AccountAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # form = UserChangeForm
    # add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('id','邮箱','姓名','用户组','是否激活')
    list_filter = ('id','email', 'name','groups','is_active')
    fieldsets = (
        ('test', {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active','groups')}),
        ('AuditPermission', {'fields': ('bind_host_users','host_groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('user_permissions','groups','bind_host_users','host_groups')


# class HostUserAdmin(BaseAdmin):
#     list_display = ['username','auth_type','password']

class HostInfoAdmin(BaseAdmin):
    list_display = ('id','hostname', 'ip_address', 'host_group','pod_count', 'idc','host_active')
    list_filter = ('ID','主机名','IP地址','主机组','容器数量','机房','连接')
    search_fields = ['hostname', 'ip_address',]
    list_per_page = 5
    filter_horizontal = ('hostname', 'ip_address', 'port', 'idc','system_user', )

    def test(self,*args,**kwargs):
        print('admin',self,args,kwargs)

class HostGroupAdmin(BaseAdmin):
    list_display = ('group_name','host_count','remark',)
    list_filter = ('主机组','主机数量','备注',)
    search_fields = ['group_name',]
# Now register the new UserAdmin...

class MonitorInfo():
    list_display = ('ip_address','cpu_use','ram_use','disk_use','host_input','host_output',)
    list_filter = ('主机','CPU使用率','内存使用率','硬盘使用率','入口流量','出口流量',)
    list_per_page = 50

class IDCInfo(BaseAdmin):
    list_display = ('name','address')
    list_filter = ('机房名称','所在位置')
    search_fields = ['name','address']

class NameSpacesInfo(BaseAdmin):
    list_display = ("name","remark")
    list_filter = ("项目名称","备注")

class MasterInfo(BaseAdmin):
    list_display = ("host","status","roles","version",'namespaces')
    list_filter = ("主机名","状态",'角色','版本','项目名称')
    search_fields=['status','roles','version','namespaces']

class PodInfo(BaseAdmin):
    list_display = ("name","container_id",'pod_ip','host_ip','host_port','namespaces','pod_status')
    list_filter = ("名字","容器ID",'PodIP','主机','对外端口','命名空间','运行状态')
    search_fields=['name','pod_status']

site.register(models.Host,HostInfoAdmin)
site.register(models.HostGroup,HostGroupAdmin)
site.register(models.Account, AccountAdmin)
site.register(models.IDC,IDCInfo)
site.register(models.Monitor,MonitorInfo)
site.register(models.AuditLog)
site.register(models.NameSpaces,NameSpacesInfo)
site.register(models.Master,MasterInfo)
site.register(models.Pod,PodInfo)


