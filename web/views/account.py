from django.shortcuts import render
from web.forms.account import RegisterModelForm,SendSmsForm,LoginSmsForm

from django.http import JsonResponse

def register(request):
    # 用户信息注册
    if request.method=='GET':
        form=RegisterModelForm(request)
        return render(request,'register.html', {'form':form})
    form=RegisterModelForm(request,data=request.POST)
    if form.is_valid():
        # 保存数据
        form.save()
        return JsonResponse({'status':True, 'data':'/web/login/'})
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
        return JsonResponse({'status':True, 'data':'/index/'})
    return JsonResponse({'status':False, 'error':form.errors})