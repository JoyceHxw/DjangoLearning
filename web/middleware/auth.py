from django.utils.deprecation import MiddlewareMixin
from web import models

from django.shortcuts import redirect
from django.conf import settings

class AuthMiddleware(MiddlewareMixin):
    def process_request(self,request):
        user_id=request.session.get('user_id',0)
        request.user_obj=models.UserInfo.objects.filter(id=user_id).first()
        if request.path_info in settings.WHITE_REGEX_URL_LIST:
            return None
        if not request.user_obj:
            return redirect('/web/login/')
        