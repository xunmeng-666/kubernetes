"""kubernetes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from host_monitor import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'^accounts/login/$', views.account_login),
    url(r'^accounts/logout/$', views.account_logout),
    url(r'^host_monitor_list/', views.host_monitor_list),
    url(r'^host_list/$', views.host_list),
    url(r'^master_ns_list/$', views.namespace),
    url(r'^master_ns_add/(\w+)/(\w+)/', views.master_ns_add),
    url(r'^pod_monitor/$', views.pod_list),
    url(r'^master_monitor/$', views.master_list),
    url(r'^host_master_add/(\w+)/(\w+)/', views.master_add),
    url(r'^idc/$', views.idc),
    url(r'^host_group/', views.hosts_group),
    url(r'^host_user/', views.host_user),
    url(r'^host_group_add/(\w+)/', views.host_group_add),
    url(r'^change_password/', views.change_password_obj),
    url(r'^host_group_edit/(\w+)/(\w+)/', views.table_group_edit),
    url(r'^host_group_del/(\w+)/(\w+)/', views.table_group_del),
    url(r'^host_add/(\w+)/(\w+)/', views.table_obj_add,name='table_obj_add'),
    url(r'^host_idc_add/(\w+)/(\w+)/', views.table_idc_add,name='table_obj_add'),
    url(r'^host_edit/(\w+)/(\w+)/(\w+)/', views.table_obj_edit,name='table_obj_edit'),
    url(r'^host_conn/(\w+)/(\w+)/(\w+)/$', views.table_obj_conn),
    url(r'^host_del/(\w+)/(\w+)/(\w+)/', views.table_obj_del),
    url(r'^host_auto_del/(\w+)/(\w+)/$', views.table_auto_del),
    url(r'^host_auto_conn/(\w+)/(\w+)/', views.host_auto_conn),
]
