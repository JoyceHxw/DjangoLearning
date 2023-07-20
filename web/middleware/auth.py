from django.utils.deprecation import MiddlewareMixin
from web import models

from django.shortcuts import redirect
from django.conf import settings

from datetime import datetime

class AuthMiddleware(MiddlewareMixin):
    def process_request(self,request):
        # 用户信息
        # 从会话中获取用户的 user_id，如果不存在则返回默认值 0。
        user_id=request.session.get('user_id',0)
        user_obj=models.UserInfo.objects.filter(id=user_id).first()
        request.user_obj=user_obj
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return None
        if not request.user_obj:
            return redirect('/web/login/')
        
        # 价格策略
        obj=models.Transaction.objects.filter(user=user_obj, status=2).order_by('-id').first()
        current_datetime=datetime.now()
        if obj.end_datetime and obj.end_datetime<current_datetime:
            obj=models.Transaction.objects.filter(user=user_obj,status=2,price_policy_category=1).first()
        request.price_policy=obj.price_policy
    
    def process_view(self,request, view, args, kwargs,):
        # 判断URL是否是以manage开头，如果是则判断项⽬ID是否是我创建 or 参与
        if not request.path_info.startswith('/web/manage/'):
            return
        project_id = kwargs.get('project_id')
        # 是否是我创建的
        project_object = models.Project.objects.filter(creator=request.user_obj, id=project_id).first()
        if project_object:
            # 是我创建的项⽬的话，我就让他通过
            request.project = project_object
            return
        # 是否是我参与的项⽬
        project_user_object = models.ProjectUser.objects.filter(user=request.user_obj, project_id=project_id).first()
        if project_user_object:
            # 是我参与的项⽬
            request.project = project_user_object.project
            return
        return redirect('project_list')