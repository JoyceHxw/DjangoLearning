from web.forms.account import RegisterModelForm,SendSmsForm,LoginSmsForm,LoginForm
from web import models

from django.http import JsonResponse

from utils.image_code import check_code
from io import BytesIO

from django.shortcuts import redirect, render,HttpResponse
from django.db.models import Q

import uuid
from datetime import datetime

# request参数是一个包含了客户端请求信息的HttpRequest对象
def register(request):
    # 用户信息注册
    # GET请求：数据包含在URL的查询参数中，出现在URL的末尾
    # POST请求：数据包含在请求体中，并不显示在URL中
    if request.method=='GET':
        form=RegisterModelForm(request)
        return render(request,'register.html', {'form':form})
    form=RegisterModelForm(request,data=request.POST)
    if form.is_valid():
        # 保存数据
        instance=form.save()
        # 生成交易记录
        policy_object=models.PricePolicy.objects.filter(category=1,title='个人免费版').first()
        models.Transaction.objects.create(
            status=2,
            order=str(uuid.uuid4()),
            user=instance,
            price_policy=policy_object,
            count=0,
            price=0,
            start_datetime=datetime.now()
        )
        return JsonResponse({'status':True, 'data':'/web/login'})
    return JsonResponse({'status':False, 'error':form.errors})


def send_sms(request):
    """ 
    发送短信
    """
    form=SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'error':form.errors})

def login_sms(request):
    if request.method=='GET':
        form=LoginSmsForm(request)
        return render(request,'login_sms.html',{'form':form})
    form=LoginSmsForm(request,data=request.POST)
    if form.is_valid():
        mobile_phone=form.cleaned_data['mobile_phone']
        user_obj=models.UserInfo.objects.filter(mobile_phone=mobile_phone).first()
        request.session['user_id']=user_obj.id
        request.session['username']=user_obj.username
        request.session.set_expiry(60*60*24*14)
        return JsonResponse({'status':True, 'data':'/web/index/'})
    return JsonResponse({'status':False, 'error':form.errors})

def login(request):
    if request.method=='GET':
        form=LoginForm(request)
        return render(request,'login.html',{'form':form})
    form=LoginForm(request,data=request.POST)
    if form.is_valid():
        username=form.cleaned_data['username']
        password=form.cleaned_data['password']
        user_object=models.UserInfo.objects.filter(Q(email=username)|Q(mobile_phone=username)).filter(password=password).first()
        if user_object:
            request.session['user_id']=user_object.id
            request.session['username']=user_object.username
            request.session.set_expiry(60*60*24*14)
            return redirect('/web/index/')
        form.add_error('username','用户名或密码错误')
    return render(request,'login.html',{'form':form})

def image_code(request):
    image_obj, code=check_code()
    request.session['image_code']=code
    request.session.set_expiry(60)

    stream=BytesIO()
    image_obj.save(stream,'png')
    return HttpResponse(stream.getvalue())

def logout(request):
    request.session.flush()
    return redirect('/web/index/')