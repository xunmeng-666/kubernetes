from django.shortcuts import render,redirect,HttpResponse
from host_monitor import core_system,forms
from host_monitor.admin_base import site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q


import json,getpass




print("注册的admin list:",site.registered_admins)
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@login_required
def change_password_obj(request):
    print('个人信息')
    if request.method == 'GET':
        return redirect("/")
    elif request.method == "POST":
        user = request.user
        pwd = request.POST.get('pwd')
        new_pwd = request.POST.get("new_pwd")
        re_pwd = request.POST.get("re_pwd")

        obj = authenticate(username=user,password=pwd)
        # obj = models.UserInfo.objects.filter(username=user, password=pwd).first()
        ret = {'status': True, 'error': None}

        if obj:
            # 密码验证成功,验证新密码
            if new_pwd == re_pwd:
                obj.set_password(new_pwd)
                obj.save()
                return HttpResponse(json.dumps(ret))
            else:
                ret['status'] = False
                ret['error'] = "新密码不一致"
                return HttpResponse(json.dumps(ret))
        else:
            ret['status'] = False
            ret['error'] = "原密码错误"
            # 登陆失败，页面显示错误信息
            return HttpResponse(json.dumps(ret))
    return redirect('/')


def account_login(request):
    print('登录界面')
    if request.method == "POST":
        print('POST请求')
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username,password=password)

        if user:
            print('user login scuess',user)
            # request.session.set_expiry(0)
            # request.session['username'] = username
            login(request,user)

            return  redirect(request.GET.get('next') or '/')
        else:
            print('密码错误')
    return render(request, 'login.html', locals())

def account_logout(request,**kwargs):
    print('注销操作')
    request.session.clear()
    logout(request)

    return redirect('/')

def get_redis_data(request,app_name,model_name,obj_id):
    if app_name in site.registered_admins:
        if model_name in site.registered_admins[app_name]:
            admin_class = site.registered_admins[app_name][model_name]
            obj = admin_class.model.objects.get(id=obj_id)
            redis_data = core_system.conn_action(obj,obj_id)
            print('redis_data',redis_data)
            ret = {'status': True, 'error': None}
            if redis_data:
                return HttpResponse(json.dumps(ret))
            else:
                return HttpResponse(json.dumps(ret))


@login_required
def index(request,**kwargs):
    ''' 获取Master/Node /Namespace/Pod数量 '''
    print('index 页面',)
    username = request.session.get('username',request.user.name)
    admin_class = admin_func().get('master')
    objects = admin_class.model.objects.all()
    host_func = admin_func().get("host")
    host_obj = host_func.model.objects.all()
    ns_count = 0
    master_count = 0
    node_count = 0
    pod_count = 0
    for obj_master in objects.values("id").distinct():
        obj_count = obj_master.get("id")
        if obj_count != None:
            master_count += 1
    for obj_ns in objects.values("namespaces__name").distinct():
        obj_count = obj_ns.get('namespaces__name')
        if obj_count != None:
            ns_count += 1
    for obj_node in host_obj.values("ip_address").distinct():
        obj_count = obj_node.get("ip_address")
        if obj_count != None:
            node_count += 1
    for obj_pod in host_obj.values("pod__pod_ip").distinct():
        obj_count = obj_pod.get("pod__pod_ip")
        if obj_count != None:
            pod_count += 1

    return render(request, 'index.html', locals())




def get_filter_objs(request,admin_class):
    """返回filter的结果queryset"""
    print('request--objs--',request)
    print('admin_class-objs--',admin_class)

    filter_condtions = {}
    for k,v in request.GET.items():
        #print(k,v)
        if k in ['_page','_q','_o']:
            continue
        if v:#valid condtion
            filter_condtions[k] = v
            print('v', v)
            print('filter_condtions[k]', filter_condtions[k])
            print('filter_condtions', filter_condtions)
    queryset = admin_class.model.objects.filter(**filter_condtions)
    print('filter con',filter_condtions)
    return queryset,filter_condtions

def get_search_objs(request,querysets,admin_class):
    """
    1.拿到_q的值
    2.拼接Q查询条件
    3.调用filter(Q条件)查询
    4. 返回查询结果
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    print('adminclass--objs--',admin_class)
    q_val = request.GET.get('_q') #None
    if q_val:
        q_obj = Q()
        q_obj.connector = "OR"
        for search_field in admin_class.search_fields: #2
            q_obj.children.append( ("%s__contains" %search_field,q_val) )
        print("serach obj",q_obj)

        search_results = querysets.filter(q_obj)#3
    else:
        search_results = querysets

    return search_results,q_val

def get_orderby_objs(request,querysets):
    """
    排序
    1.获取_o的值
    2.调用order_by(_o的值)
    3.处理正负号，来确定下次的排序的顺序
    4.返回
    :param request:
    :param querysets:
    :return:
    """
    print('request--get-objs',request)
    print('querysets--get-objs',querysets)
    orderby_key = request.GET.get('_o') #-id
    last_orderby_key = orderby_key or ''
    if orderby_key:
        order_column = orderby_key.strip('-')
        order_results = querysets.order_by(orderby_key)
        #new_order_key =
        # if request.GET.get('_page'):#代表有分页，不对_o的值取反
        #     print("不取反",orderby_key)
        #     new_order_key = orderby_key
        # else:
        if orderby_key.startswith('-'):
            new_order_key = orderby_key.strip('-')
        else:
            new_order_key = "-%s"% orderby_key

        return order_results,new_order_key,order_column,last_orderby_key
    else:
        return querysets,None,None,last_orderby_key

def admin_func():
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name]
        return admin_class


@login_required
def host_list(request,no_render=False):
    print('request--hostlist',request)
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name].get("host")
        model_name = admin_class.model._meta.model_name
        print('admin-class',admin_class.list_display)
        if request.method == "POST":  # admin action
            action_func_name = request.POST.get('admin_action')

            action_func = getattr(admin_class, action_func_name)

            print(request.POST)
            selected_obj_ids = request.POST.getlist("_selected_obj")
            selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
            action_res = action_func(request, selected_objs)
            if action_res:
                return action_res
            return redirect(request.path)
        else:
            # print("--model class",model_class,locals())
            querysets, filter_conditions = get_filter_objs(request, admin_class)
            print('fitler_condi--*', filter_conditions)
            print("filte---", querysets)
            print("admin_class1---", admin_class)
            querysets, q_val = get_search_objs(request, querysets, admin_class)
            print('q_val', q_val)
            print('request--get',request)
            querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

            paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
            page = request.GET.get('_page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                querysets = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                querysets = paginator.page(paginator.num_pages)
        if no_render:  # 被其它函数调用，只返回数据
            return locals()
        else:
        # querysets, filter_condtions = get_filter_objs(request, admin_class)
            return render(request, 'list/host_list.html', locals())

@login_required
def pod_list(request,no_render=False):
    admin_class = admin_func().get("pod")
    print('admin-class', admin_class.list_display)
    if request.method == "POST":  # admin action
        action_func_name = request.POST.get('admin_action')

        action_func = getattr(admin_class, action_func_name)

        print(request.POST)
        selected_obj_ids = request.POST.getlist("_selected_obj")
        selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
        action_res = action_func(request, selected_objs)
        if action_res:
            return action_res
        return redirect(request.path)
    else:
        # print("--model class",model_class,locals())
        querysets, filter_conditions = get_filter_objs(request, admin_class)
        print('fitler_condi--*', filter_conditions)
        print("filte---", querysets)
        print("admin_class1---", admin_class)
        querysets, q_val = get_search_objs(request, querysets, admin_class)
        print('q_val', q_val)
        print('request--get', request)
        querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

        paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
        page = request.GET.get('_page')
        try:
            querysets = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            querysets = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            querysets = paginator.page(paginator.num_pages)
    if no_render:  # 被其它函数调用，只返回数据
        return locals()
    else:
        # querysets, filter_condtions = get_filter_objs(request, admin_class)
        return render(request, 'pod_list.html', locals())

@login_required
def master_list(request,no_render=False):
    # admin_class = admin_func().get("master")
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name].get('master')
        model_name = admin_class.model._meta.model_name
        print('master_model_name',model_name)
        if request.method == "POST":  # admin action
            action_func_name = request.POST.get('admin_action')

            action_func = getattr(admin_class, action_func_name)

            print(request.POST)
            selected_obj_ids = request.POST.getlist("_selected_obj")
            selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
            action_res = action_func(request, selected_objs)
            if action_res:
                return action_res
            return redirect(request.path)
        else:
            print("GET请求")

            querysets, filter_conditions = get_filter_objs(request, admin_class)
            print('fitler_condi--*', filter_conditions)
            print("filte---", querysets)
            # print("admin_class1---", admin_class)
            querysets, q_val = get_search_objs(request, querysets, admin_class)
            print('q_val', q_val)
            print('request--get',querysets)

            querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

            paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
            page = request.GET.get('_page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                querysets = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                querysets = paginator.page(paginator.num_pages)

        if no_render:  # 被其它函数调用，只返回数据
            return locals()
        else:
        # querysets, filter_condtions = get_filter_objs(request, admin_class)
            return render(request, 'list/master_list.html', locals())


@login_required
def namespace(request,no_render=False):
    print('request--hostlist',request)
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name].get("namespaces")
        model_name = admin_class.model._meta.model_name
        print('admin-class',admin_class.list_display)
        if request.method == "POST":  # admin action
            action_func_name = request.POST.get('admin_action')

            action_func = getattr(admin_class, action_func_name)

            print(request.POST)
            selected_obj_ids = request.POST.getlist("_selected_obj")
            selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
            action_res = action_func(request, selected_objs)
            if action_res:
                return action_res
            return redirect(request.path)
        else:
            # print("--model class",model_class,locals())
            querysets, filter_conditions = get_filter_objs(request, admin_class)
            print('fitler_condi--*', filter_conditions)
            print("filte---", querysets)
            print("admin_class1---", admin_class)
            querysets, q_val = get_search_objs(request, querysets, admin_class)
            print('q_val', q_val)
            print('request--get',request)
            querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

            paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
            page = request.GET.get('_page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                querysets = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                querysets = paginator.page(paginator.num_pages)
        if no_render:  # 被其它函数调用，只返回数据
            return locals()
        else:
        # querysets, filter_condtions = get_filter_objs(request, admin_class)
            return render(request, 'list/host_list.html', locals())

@login_required
def master_ns_add(request,app_name,model_name):
    # print('admin_class-ADD',admin_class)
    admin_class = admin_func().get('namespaces')
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "GET":
        print('IS GET')
        form_obj = form()
        print('form_obj-GET',form_obj)
        for field in form_obj:
            print('field-dir',dir(field.field))
            print('field-dir-verbose_name',field.label)
    elif request.method == "POST":
        print('is post----')
        form_obj = form(data=request.POST)
        print('命名空间form-obj----',form_obj)
        print('验证命名空间')
        if form_obj.is_valid():
            print('验证通过，开始保存')
            form_obj.save()
            print('命名空间保存成功，跳转至主机组页面')
            return redirect('/master_ns_list/')
        else:
            print('命名空间信息验证失败')
    return render(request, 'list/master_ns_add.html', locals())

@login_required
def idc(request,no_render=False):

    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name].get('idc')
        model_name = admin_class.model._meta.model_name
        if request.method == "POST":  # admin action
            action_func_name = request.POST.get('admin_action')

            action_func = getattr(admin_class, action_func_name)

            print(request.POST)
            selected_obj_ids = request.POST.getlist("_selected_obj")
            selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
            action_res = action_func(request, selected_objs)
            if action_res:
                return action_res
            return redirect(request.path)
        else:
            print("GET请求")

            querysets, filter_conditions = get_filter_objs(request, admin_class)
            print('fitler_condi--*', filter_conditions)
            print("filte---", querysets)
            # print("admin_class1---", admin_class)
            querysets, q_val = get_search_objs(request, querysets, admin_class)
            print('q_val', q_val)
            print('request--get', querysets)

            querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

            paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
            page = request.GET.get('_page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                querysets = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                querysets = paginator.page(paginator.num_pages)

        if no_render:  # 被其它函数调用，只返回数据
            return locals()
        else:
            # querysets, filter_condtions = get_filter_objs(request, admin_class)
            return render(request, 'list/idc.html', locals())

@login_required
def table_group_edit(request,app_name,object_id):
    print('编辑',request)
    # print('admin_class',admin_class)
    # print('admin_class类型',type(admin_class))
    print('object_id',object_id)
    # admin_class = admin_func().get('hostgroup')
    if app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name].get('hostgroup')
        object = admin_class.model.objects.get(id=object_id)
        form = forms.create_dynamic_modelform(admin_class.model)
        print('form--',form())
        print('form--',dir(form()))
        if request.method == "GET":
            print('编辑---GET',form())
            form_obj = form(instance=object)
        elif request.method == "POST":
            print('编辑---POST')
            form_obj = form(instance=object,data=request.POST)
            print('编辑---form_obj',form_obj.is_valid())
            if form_obj.is_valid():
                print('执行保存---')
                form_obj.save()
                return redirect('/host_group/')
            print('保存失败--')
    return render(request, 'host_info/table_object_change.html', locals())

@login_required
def table_group_del(request,app_name,model_name,obj_name):
    print('删除操作',request.method)
    if app_name in site.registered_admins:
        if model_name in site.registered_admins[app_name]:
            admin_class = site.registered_admins[app_name][model_name]
            obj = admin_class.model.objects.get(id=obj_name)
            print('obj-dir--',dir(obj))
            obj.delete()

    return redirect('/host_group/')

@login_required
def table_obj_edit(request,app_name,model_name,object_id):
    print('编辑',request)

    if app_name in site.registered_admins:
        if model_name in site.registered_admins[app_name]:
            admin_class = site.registered_admins[app_name][model_name]
            object = admin_class.model.objects.get(id=object_id)
            form = forms.create_dynamic_modelform(admin_class.model)
            print('form--',form())
            print('form--',dir(form()))
            if request.method == "GET":
                print('编辑---GET',form())
                form_obj = form(instance=object)
                print('form_obj-----',form_obj.instance)
                print('form_obj-----',dir(form_obj.instance))

            elif request.method == "POST":
                print('编辑---POST')
                form_obj = form(instance=object,data=request.POST)
                print('编辑---form_obj',form_obj.is_valid())
                if form_obj.is_valid():
                    print('执行保存---')
                    form_obj.save()
                    return redirect('/host_list/')
                print('保存失败--')
    return render(request, 'list/host_edit.html', locals())
    # return  locals()

@login_required
def table_idc_add(request,app_name,model_name):
    print('request',request)
    print('app_name',app_name)
    print('model_name',model_name)

    admin_class = admin_func().get('idc')
    print('admin_class-',admin_class)
    form = forms.create_dynamic_modelform(admin_class.model)
    print('form--',form())

    if request.method == "GET":
        print('IS GET')
        form_obj = form()
        print('form_obj-GET',form_obj)
    elif request.method == "POST":
        print('is post----')
        form_obj = form(data=request.POST)
        print('form-obj',form_obj.is_valid())
        if form_obj.is_valid():
            print('form_obj--save',form_obj.save)
            form_obj.save()

            print('POST 执行return',form_obj)
            return redirect("/idc/")
    print('GET 执行return')
    return render(request, 'list/idc_add.html', locals())
    # return render(request, 'host_info/table_object_add.html', locals())



@login_required
def table_obj_add(request,app_name,model_name,):
    print('request',request)
    print('app_name',app_name)
    print('model_name',model_name)
    if app_name in site.registered_admins:
        print('app_name in site')
        # if model_name in site.registered_admins[app_name]:
        #     print('model_name in site[app_name]')
        admin_class = site.registered_admins[app_name][model_name]
        print('admin_class-',admin_class)
        form =forms.create_dynamic_modelform(admin_class.model)
        print('form--',form())

        if request.method == "GET":
            print('IS GET')
            form_obj = form()
            for field in form_obj:
                print(dir(field))
                print('data',field.data)
                print('html_name',field.html_name)

        elif request.method == "POST":
            print('is post----')
            form_obj = form(data=request.POST)

            print('form-obj',form_obj.is_valid())
            if form_obj.is_valid():
                print('form_obj--save',form_obj.save)
                form_obj.save()

                print('POST 执行return',form_obj)
                return redirect("/host_list/")
        print('GET 执行return')
    return render(request, 'list/host_add.html', locals())

@csrf_exempt
@login_required
def host_monitor_list(request):

    print('request',request)
    admin_class = admin_func().get('monitor')
    monitor_data = admin_class.model.objects.all()
    print('获取主机列表')
    host_list = monitor_data.values('hostname__ip_address').distinct()
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "GET":
        form_obj = form()
    elif request.method == "POST":
        print('POST请求')
        print('定义当前时间')

        print('获取主机IP')
        host_ip = request.POST.get("host_ip")
        print("获取时间")
        data_func = request.POST.get("func_data")
        print("获取到的时间:",data_func)
        if data_func == 'now_data':
            print('开始获取主机ID')
            id_list = monitor_data.filter(hostname__ip_address=host_ip).values('id').last()
            print("主机ID获取成功，开始获取数据")
            data = {}
            for index, id_info in enumerate(id_list):
                host_info = monitor_data.filter(id=id_list.get('id'))
                print('host_info----',host_info)
                for info in host_info:
                    cpu_use = info.cpu_use
                    ram_use = info.ram_use.split('%')[0]
                    disk_use = info.disk_use.split('%')[0]
                    host_input = info.host_input
                    host_output = info.host_output
                    time = info.date.strftime('%Y-%m-%d %H:%M:%S')
                    data.update({index: {'cpu_use': cpu_use, 'ram_use': ram_use, 'disk_use': disk_use,
                                         'host_input': host_input, 'host_output': host_output, 'host_date': time}})

            print('data数据2', data)
            return HttpResponse(json.dumps(data))

        elif data_func == 'three_data':
            print("主机ID获取成功，开始获取主机3天数据")
            day_count = 3
            host_date = date_function(monitor_data,host_ip,day_count)
            print('3天数据',host_date)
            return HttpResponse(json.dumps(host_date))
        elif data_func == 'seven_data':
            print("主机ID获取成功，开始获取主机3天数据")
            day_count = 7
            host_date = date_function(monitor_data,host_ip,day_count)
            print('7天数据',host_date)
            return HttpResponse(json.dumps(host_date))
        elif data_func == 'thirty_data':
            print("主机ID获取成功，开始获取主机30天数据")
            day_count = 30
            host_date = date_function(monitor_data, host_ip, day_count)
            print('30天数据', host_date)
            return HttpResponse(json.dumps(host_date))
    return render(request, 'list/host_monitor_list.html', locals())

def date_function(monitor_data,host_ip,day_count):
    print('day_count',day_count)
    print('主机:',host_ip)
    import datetime
    now_data = datetime.datetime.now()
    print('开始获取主机ID')
    host_id = []
    id_list = monitor_data.filter(hostname__ip_address=host_ip).values('id','date')
    for id_info in id_list:
        if id_info.get("date").day > now_data.day - day_count:
            host_id.append(id_info.get("id"))
    data = {}
    for index,id_info in enumerate(host_id):
        host_info = monitor_data.filter(id=id_info)
        for info in host_info:
            cpu_use = info.cpu_use
            ram_use = info.ram_use.split('%')[0]
            disk_use = info.disk_use.split('%')[0]
            host_input = info.host_input
            host_output = info.host_output
            # time = info.date.strftime('%Y-%m-%d %H:%M:%S')
            time = info.date.strftime('%Y-%m-%d')
            data.update({index: {'cpu_use': cpu_use, 'ram_use': ram_use, 'disk_use': disk_use,
                                 'host_input': host_input, 'host_output': host_output, 'host_date': time}})
        print('data数据1', data)
    print('data数据2', data)
    return data





@csrf_exempt
@login_required
def table_obj_conn(request,app_name,model_name,obj_name):
    print('request--conn',request)

    if app_name in site.registered_admins:
        if model_name in site.registered_admins[app_name]:
            admin_class = site.registered_admins[app_name][model_name]
            print('admin_class',admin_class)
            # print('get_id', obj_id)

            obj = admin_class.model.objects.get(id=obj_name)
            print("obj-dir--", obj)
            obj_class = core_system.conn_paramiko(obj)
            # obj_class = core_system.Redis_db(obj)
            ret = {'status': True, 'error': None}
            if obj_class:
                obj.enabled = 1
                obj.save()

                print('连接成功')
                return HttpResponse(json.dumps(ret))

            else:
                print('连接失败')
                ret['status'] = False
                ret['error'] = "密码错误"
                # 客户端连接失败
                return HttpResponse(json.dumps(ret))

@csrf_exempt
@login_required
def host_auto_conn(request,app_name,model_name):
    print('reqeust',request)
    # print('reqeust---',request.GET.get('idAll').split(','))

    if app_name in site.registered_admins:
        if model_name in site.registered_admins[app_name]:
            admin_class = site.registered_admins[app_name][model_name]
            for obj_id in request.GET.get('idAll').split(','):

                print('get_id',obj_id)

                obj = admin_class.model.objects.get(id=obj_id)
                print("obj-dir--",obj)
                obj_class = core_system.conn_paramiko(obj)
                ret = {'status': True, 'error': None}

                if obj_class:
                    obj.enabled = 1
                    obj.save()

                    print('连接成功')
                    return HttpResponse(json.dumps(ret))

                else:
                    print('连接失败')
                    ret['status'] = False
                    ret['error'] = "密码错误"
                    # 客户端连接失败
                    return HttpResponse(json.dumps(ret))

    # return redirect('/list/',locals())

@login_required
def table_obj_del(request,app_name,model_name,obj_name):
    print('删除操作',request.method)
    if app_name in site.registered_admins:
        if model_name in site.registered_admins[app_name]:
            admin_class = site.registered_admins[app_name][model_name]
            obj = admin_class.model.objects.get(id=obj_name)
            print('obj-dir--',dir(obj))
            obj.delete()

    return redirect('/host_list/')

@login_required
def table_auto_del(request,app_name,model_name):
    try:
        print('request',request.GET.get('idAll').split(','))
        for get_id in request.GET.get('idAll').split(','):
            print('GET--',get_id)
            for obj_id in get_id.split(","):
                print('get--1',obj_id)
                if app_name in site.registered_admins:
                    print('app_name',app_name)
                    if model_name in site.registered_admins[app_name]:
                        print('model-name',model_name)
                        admin_class = site.registered_admins[app_name][model_name]
                        print('admin_class',admin_class)
                        obj = admin_class.model.objects.get(id=get_id)
                        print('obj-dir--', dir(obj))
                        obj.delete()
    except ValueError:
        pass
    return redirect('/host_list/')


@login_required
def host_user(request,no_render=None,model_name='account'):

    # print('model_name',model_name)
    for app_name in site.registered_admins:
        if app_name in site.registered_admins:
            admin_class = site.registered_admins[app_name].get('account')
            admin_model_name = admin_class.model._meta.verbose_name
            admin_display = admin_class.list_display
            admin_list_filter = admin_class.list_filter
            querysets, filter_condtions = get_filter_objs(request, admin_class)
            print('querysets',querysets)
            print('admin-class', admin_class.list_display)
            print(request)
            if request.method == "POST":  # admin action
                print('request',dir(request.POST.get))
                action_func_name = request.POST.get('admin_action')
                action_func = getattr(admin_class, action_func_name)
                print(request.POST)
                selected_obj_ids = request.POST.getlist("_selected_obj")
                selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
                action_res = action_func(request, selected_objs)
                if action_res:
                    return action_res
                return redirect(request.path)
            else:
                # print("--model class",model_class,locals())
                querysets, filter_conditions = get_filter_objs(request, admin_class)
                print('fitler_condi--*', filter_conditions)
                print("filte---", querysets)
                print("admin_class1---", admin_class)
                querysets, q_val = get_search_objs(request, querysets, admin_class)
                print('q_val', q_val)
                print('request--get', request)
                querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

                paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
                page = request.GET.get('_page')
                try:
                    querysets = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    querysets = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    querysets = paginator.page(paginator.num_pages)
            if no_render:  # 被其它函数调用，只返回数据
                return locals()
            else:
                # querysets, filter_condtions = get_filter_objs(request, admin_class)
                return render(request, 'host_setting/user_list.html', locals())
    return render(request, 'host_setting/user_list.html', locals())
    # return HttpResponse('功能开发中......')

@login_required
def host_settings(request):
    # print('request--setting',request)
    return HttpResponse('功能开发中......')



@login_required
def hosts_group(request,no_render=None):
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name].get('hostgroup')
    # admin_class = admin_func().get('hostgroup')
        model_name = admin_class.model._meta.model_name
        print('model_name---',model_name)
        print('group-admin_class',admin_class)

        update = update_group(admin_class)

        if request.method == "POST":  # admin action
            action_func_name = request.POST.get('admin_action')

            action_func = getattr(admin_class, action_func_name)

            print(request.POST)
            selected_obj_ids = request.POST.getlist("_selected_obj")
            selected_objs = admin_class.model.objects.filter(id__in=selected_obj_ids)
            action_res = action_func(request, selected_objs)
            if action_res:
                return action_res
            return redirect(request.path)
        else:
            print("GET请求")

            querysets, filter_conditions = get_filter_objs(request, admin_class)
            print('fitler_condi--*', filter_conditions)
            print("filte---", querysets)
            # print("admin_class1---", admin_class)
            querysets, q_val = get_search_objs(request, querysets, admin_class)
            print('q_val', q_val)
            print('request--get', querysets)

            querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)

            paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
            page = request.GET.get('_page')
            try:
                querysets = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                querysets = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                querysets = paginator.page(paginator.num_pages)

        if no_render:  # 被其它函数调用，只返回数据
            return locals()
        else:
            # querysets, filter_condtions = get_filter_objs(request, admin_class)
            return render(request, 'list/host_group.html', locals())

def update_group(admin_class):
    print('开始update')
    obj = admin_class.model.objects.all()
    try:
        for host in obj.values('id'):
            obj.filter(id=host.get('id')).update(host_count=obj.filter(host__host_group_id=host.get('id')).count())
    except Exception:
        pass

@login_required
def sys_settings(reuquest):
    return HttpResponse('功能开发中......')

@login_required
def host_group_add(request,app_name):
    # print('admin_class-ADD',admin_class)
    admin_class = admin_func().get('hostgroup')
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "GET":
        print('IS GET')
        form_obj = form()
        print('form_obj-GET',form_obj)
        for field in form_obj:
            print('field-dir',dir(field.field))
            print('field-dir-verbose_name',field.label)
    elif request.method == "POST":
        print('is post----')
        form_obj = form(data=request.POST)
        print('主机组form-obj----',form_obj)
        print('验证主机组信息')
        if form_obj.is_valid():
            print('验证通过，开始保存')
            form_obj.save()
            print('主机组保存成功，跳转至主机组页面')
            return redirect('/host_group/')
        else:
            print('主机组信息验证失败')
    return render(request, 'list/host_group_add.html', locals())


@login_required
def master_add(request,app_name,model_name):
    print('集群app_name',app_name)
    print('集群model_name',model_name)
    admin_class = admin_func().get('master')
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == "GET":
        print('IS GET')
        form_obj = form()
        print('form_obj-GET',form_obj)
        for field in form_obj:
            print('field-dir',dir(field.field))
            print('field-dir-verbose_name',field.label)
    elif request.method == "POST":
        print('is post----')
        form_obj = form(data=request.POST)
        print('集群form-obj----',form_obj)
        print('验证集群信息')
        if form_obj.is_valid():
            print('验证通过，开始保存')
            form_obj.save()
            print('集群信息保存成功，跳转至主机组页面')
            return redirect('/host_group/')
        else:
            print('集群信息验证失败')
    return render(request, 'list/host_group_add.html', locals())

@login_required
def host_inform(request):
    return render(request, 'monitor/inform.html')


