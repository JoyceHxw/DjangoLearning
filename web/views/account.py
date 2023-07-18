from django.shortcuts import render,HttpResponse
from web.forms.account import RegisterModelForm

def register(request):
    # 用户信息注册
    form=RegisterModelForm()
    return render(request,'register.html', {'form':form})