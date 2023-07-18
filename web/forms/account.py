from django import forms
from django.core.validators import RegexValidator
from web import models
from django.conf import settings
from django.core.exceptions import ValidationError
import random
from utils.tencent.sms import send_sms_single

from django.shortcuts import render,HttpResponse

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

# 发送短信表单验证
class SendSmsForm(forms.Form):
    mobile_phone=forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '⼿机号格式错误'),]
    )
    print(mobile_phone.label)
    def __init__(self,request,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request=request

    def clean_mobile_phone(self):
        mobile_phone=self.cleaned_data['mobile_phone']
        # 验证短信模板
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            return ValidationError('模板不存在')
        
        # 手机号是否存在
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if exists:
            return ValidationError('手机号已存在')
        
        # 生成验证码
        code = random.randrange(1000, 9999)
        print("验证码: ",code)
        # res = send_sms_single('18681693111', template_id, [code, ])
        # if res['result'] != 0:
        #     return HttpResponse(res['errmsg'])
        self.request.session['code']=str(code)
        self.request.session.set_expiry(60)
        
        return mobile_phone
        