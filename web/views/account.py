from django.shortcuts import render
from web.forms.account import RegisterModelForm,SendSmsForm

from django.http import JsonResponse

def register(request):
    # 用户信息注册
    if request.method=='GET':
        form=RegisterModelForm(request)
        return render(request,'register.html', {'form':form})
    form=RegisterModelForm(request,data=request.POST)
    if form.is_valid():
        # 保存数据
        return JsonResponse({'statue':True, 'data':'/web/login/'})
    return JsonResponse({'status':False, 'error':form.errors})


def send_sms(request):
    """ 
    发送短信
    """
    form=SendSmsForm(request, data=request.GET)
    if form.is_valid():
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, 'error':form.errors})