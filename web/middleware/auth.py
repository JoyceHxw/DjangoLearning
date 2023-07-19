from django.utils.deprecation import MiddlewareMixin
from web import models

class AuthMiddleware(MiddlewareMixin):
    def process_request(self,request):
        user_id=request.session.get('user_id',0)
        request.user_obj=models.UserInfo.objects.filter(id=user_id).first()