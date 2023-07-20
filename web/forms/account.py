# forms是一个模块，用于帮助开发者创建和处理表单（forms）。表单是网站与用户交互的一种重要方式，允许用户提交数据并与服务器进行交互。
from django import forms
from django.core.validators import RegexValidator
from web import models
from django.conf import settings
# 当表单数据验证失败时，可以通过抛出ValidationError来指示验证失败，并在页面上显示相应的错误消息。
from django.core.exceptions import ValidationError
import random
from utils.tencent.sms import send_sms_single

from django.shortcuts import render,HttpResponse

from web.forms.bootStrap import BootStrap

class RegisterModelForm(BootStrap, forms.ModelForm):
        # 正则表达式校验
        # 定义表单字段
        mobile_phone=forms.CharField(
            label="手机号",
            # 表示手机号的第一位必须是1，后面跟着3到9中的一个数字，接下来必须是9个数字，$：表示字符串的结尾。
            validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '⼿机号格式错误'),]
        )
        password=forms.CharField(
            label='密码',
            widget=forms.PasswordInput(), # 修改密码的默认显示
            min_length=8,
            max_length=32,
            error_messages={
                # 内置的验证器
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

        # 用于定义与模型关联的表单选项的内部类
        class Meta:
            # 指定该表单与哪个模型（Model）相关联
            model=models.UserInfo
            # 生成所有字段
            # fields='__all__'
            # 选择生成表单的字段和顺序
            # 如果模型中没有相应的字段，那么表单就没有与之关联的数据存储位置，confirm_password和code不需要存储
            # 由于继承ModelForm，没有显示地定义email,username的表单字段，自动从模型中生成
            fields=['username','email','password','confirm_password','mobile_phone','code']
        
        def __init__(self,request, *args, **kwargs):
            super().__init__(*args,**kwargs)
            self.request=request
            # for name, field in self.fields.items():
                # 指定相应的小部件，attrs表示形式为文本输入 
            #   field.widget.attrs['class']='form-control'
            #   field.widget.attrs['placeholder']='请输入%s'%(field.label,)
        
        # 以下是自定义验证器
        # 验证器方法的命名规则是在字段名称前加上clean_
        def clean_username(self):
            # self.cleaned_data是一个字典，它包含了已经通过所有字段验证的数据
            username = self.cleaned_data["username"]
            exists=models.UserInfo.objects.filter(username=username).exists()
            if exists:
                # ValidationError的错误信息存储在表单对象的errors属性中
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
            # 输入的验证码
            code = self.cleaned_data["code"]
            # 使用self.cleaned_data时，如果尝试访问不存在的字段，会引发KeyError异常。
            # 使用self.cleaned_data.get时，如果该键不存在，则默认返回None（或指定的默认值）而不会引发异常。
            mobile_phone=self.cleaned_data.get('mobile_phone')
            if not mobile_phone:
                return code
            # request.session：表示用户的会话数据。Django提供了一个中间件称为"SessionMiddleware"，它负责处理会话数据的存储和管理。
            # 系统生成的验证码
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
        # 验证短信模板
        # 在html的ajax中定义了url的查询字符串参数
        tpl = self.request.GET.get('tpl')
        template_id = settings.TENCENT_SMS_TEMPLATE.get(tpl)
        if not template_id:
            raise ValidationError('模板不存在')
        
        # 手机号是否存在
        mobile_phone=self.cleaned_data['mobile_phone']
        exists=models.UserInfo.objects.filter(mobile_phone=mobile_phone).exists()
        # 登录页面也使用了验证码，需要区分
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

# 短信登录验证
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
    
# 用户名密码登录验证
class LoginForm(BootStrap,forms.Form):
    username=forms.CharField(label='邮箱或手机号')
    password=forms.CharField(
        label='密码',
        #密码回填，是指在用户提交表单时，如果验证失败，密码字段中输入的值是否会被保留在输入框中，而不是清空。
        widget=forms.PasswordInput(render_value=True) 
    )
    code=forms.CharField(label="图片验证码")

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    
    def clean_password(self):
        pwd = self.cleaned_data["password"]
        # 加密 & 返回
        # return encrypt.md5(pwd)
        return pwd
    
    def clean_code(self):
        code = self.cleaned_data["code"]
        session_code=self.request.session.get('image_code')
        if not session_code:
            raise ValidationError('验证码已过期，请重新获取')
        # 不区分大小写和空格
        if code.strip().upper()!=session_code.strip().upper():
            raise ValidationError('验证码输入错误')
        return code
    
    