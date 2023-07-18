from django.shortcuts import render,HttpResponse

# Create your views here.
import random
from utils.tencent.sms import send_sms_single
from django.conf import settings

from django import forms
from bug import models

from django.core.validators import RegexValidator

def send_sms(request):
    """ 发送短信
    根据类型使⽤不同的模版
    ?tpl=login -> 1865614
    ?tpl=register -> 1865614
    """
    tpl = request.GET.get('tpl')
    template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
    if not template_id:
        return HttpResponse('模板不存在')
    code = random.randrange(1000, 9999)
    res = send_sms_single('18681693111', template_id, [code, ])
    if res['result'] == 0:
        return HttpResponse('成功')
    else:
        return HttpResponse(res['errmsg'])
    

class RegisterModelForm(forms.ModelForm):
    # 正则表达式校验
    mobile_phone=forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '⼿机号格式错误'),]
    )
    # 修改密码的默认显示
    password=forms.CharField(
        label='密码',
        widget=forms.PasswordInput()
    )
    confirm_password=forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput()
    )
    code=forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )

    class Meta:
        model=models.UserInfo
        # 生成所有字段
        # fields='__all__'
        # 选择生成表单的字段和顺序
        fields=['username','email','password','confirm_password','mobile_phone','code']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class']='form-control'
            field.widget.attrs['placeholder']='请输入%s'%(field.label,)

def register(request):
    # 用户信息注册
    form=RegisterModelForm()
    return render(request,'register.html',{'form':form})