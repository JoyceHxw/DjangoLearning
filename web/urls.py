from django.urls import path
from web.views import account,home

urlpatterns = [
    path('register/',account.register, name='register'),
    path('sms/code/', account.send_sms, name='send_sms'),
    path('login/sms/',account.login_sms, name='login_sms'),
    path('login/',account.login, name='login'),
    path('logout/',account.logout, name='logout'),
    path('image/code/',account.image_code, name='image_code'),

    path('index/',home.index,name='index'),
    
]