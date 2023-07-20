from django.utils.deprecation import MiddlewareMixin
from web import models

from django.shortcuts import redirect
from django.conf import settings

from datetime import datetime

class AuthMiddleware(MiddlewareMixin):
    def process_request(self,request):
        # 用户信息
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