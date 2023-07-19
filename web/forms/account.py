from django import forms
from django.core.validators import RegexValidator
from web import models
from django.conf import settings
from django.core.exceptions import ValidationError
import random
from utils.tencent.sms import send_sms_single

from django.shortcuts import render,HttpResponse

from web.views.bootStrap import BootStrap

class RegisterModelForm(BootStrap, forms.ModelForm):
        # 正则表达式校验
        mobile_phone=forms.CharField(
            label="手机号",
            validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '⼿机号格式错误'),]
        )
        password=forms.CharField(
            label='密码',
            widget=forms.PasswordInput(), # 修改密码的默认显示
            min_length=8,
            max_length=32,
            error_messages={
                'min_length': "密码长度不能小于8位",
                'max_length': "密码长度不能大于32位",
            },
        )
        confirm_password=forms.CharField(
            label="重复密码",
            widget=forms.PasswordInput(),
            min_length=8,
            max_length=32,
            error_messages={
                'min_length': "密码长度不能小于8位",
                'max_length': "密码长度不能大于32位",
            },
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
        
        def __init__(self,request, *args, **kwargs):
            super().__init__(*args,**kwargs)
            self.request=request
            # for name, field in self.fields.items():
            #     field.widget.attrs['class']='form-control'
            #     field.widget.attrs['placeholder']='请输入%s'%(field.label,)
        
        def clean_username(self):
            username = self.cleaned_data["username"]
            exists=models.UserInfo.objects.filter(username=username).exists()
            if exists:
                raise ValidationError('用户名已存在')
            return username
        
        def clean_email(self):
            email = self.cleaned_data['email']
            exists = models.UserInfo.objects.filter(email=email).exists()
            if exists:
                raise ValidationError('邮箱已存在')
            return email
        
        def clean_password(self):
            pwd = self.cleaned_data["password"]
            # return encrypt.md5(pwd) //加密返回
            return pwd
        
        def clean_confirm_password(self):
            pwd = self.cleaned_data["password"]
            # 加密操作
            # confirm_pwd = encrypt.md5(self.cleaned_data['confirm_password'])
            confirm_pwd=self.cleaned_data['confirm_password']
            if pwd!=confirm_pwd:
                raise ValidationError('两次密码不一致')
            return confirm_pwd
        
        def clean_mobile_phone(self):
            mobile_phone = self.cleaned_data['mobile_phone']
            exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
            if exists:
                raise ValidationError('⼿机号已注册')
            return mobile_phone
        
        def clean_code(self):
            code = self.cleaned_data["code"]
            mobile_phone=self.cleaned_data.get('mobile_phone')
            if not mobile_phone:
                return code
            session_code=self.request.session.get('code')
            if not session_code:
                raise ValidationError("验证码失效或未发送，请重新发送")
            if code!=session_code:
                raise ValidationError("验证码错误，请重新输入")
            return code
        
        

# 发送短信表单验证
class SendSmsForm(forms.Form):
    mobile_phone=forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '⼿机号格式错误'),]
    )

    def __init__(self,request,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request=request

    def clean_mobile_phone(self):
        mobile_phone=self.cleaned_data['mobile_phone']
        # 验证短信模板
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('模板不存在')
        
        # 手机号是否存在
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if tpl=='login':
            if not exists:
                raise ValidationError('手机号不存在')
        else:
            if exists:
                raise ValidationError('手机号已存在')
        
        # 生成验证码
        code = random.randrange(1000, 9999)
        print("验证码: ",code)
        # res = send_sms_single('18681693111', template_id, [code, ])
        # if res['result'] != 0:
        #     return HttpResponse(res['errmsg'])
        self.request.session['code']=str(code)
        self.request.session.set_expiry(60)
        
        return mobile_phone

# 登录验证
class LoginSmsForm(BootStrap,forms.Form):
    mobile_phone=forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '⼿机号格式错误'),]
    )
    code=forms.CharField(
        label='验证码',
        widget=forms.TextInput()
    )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    
    def clean_mobile_phone(self):
        mobile_phone = self.cleaned_data['mobile_phone']
        exists = models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        if not exists:
            raise ValidationError('⼿机号不存在')
        return mobile_phone

    def clean_code(self):
        code = self.cleaned_data['code']
        mobile_phone = self.cleaned_data.get('mobile_phone')
        # ⼿机号不存在，则验证码⽆需再校验
        if not mobile_phone:
            return code

        session_code = self.request.session['code'] # 从session中获取验证码
        if not session_code:
            raise ValidationError('验证码失效或未发送，请重新发送')

        if code != session_code:
            raise ValidationError('验证码错误，请重新输⼊')
        return code