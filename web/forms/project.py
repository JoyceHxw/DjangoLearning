from django import forms
from web.forms.bootStrap import BootStrap

from web import models
from django.core.exceptions import ValidationError

class ProjectModelForm(BootStrap,forms.ModelForm):
    class Meta:
        model=models.Project
        fields=['name','color','desc']
        widgets={
            'desc':forms.Textarea,
        }
    
    def __init__(self,request,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.request=request
    
    # 校验项目是否存在
    def clean_name(self):
        # 校验项目是否存在
        name = self.cleaned_data["name"]
        exists=models.Project.objects.filter(name=name,creator=self.request.user_obj).exists()
        if exists:
            raise ValidationError("项目名已存在")
        
        # 校验价格策略
        count=models.Project.objects.filter(creator=self.request.user_obj).count()
        if count>=self.request.price_policy.project_num:
            raise ValidationError("项目个数超额，请购买套餐")
        return name
    