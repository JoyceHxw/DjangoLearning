from django import forms
from django.core.validators import RegexValidator
from web import models

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