from django.urls import path
from web.views import account,home,project

urlpatterns = [
    # 注册功能
    path('register/',account.register, name='register'),
    path('sms/code/', account.send_sms, name='send_sms'),
    path('login/sms/',account.login_sms, name='login_sms'),
    path('login/',account.login, name='login'),
    path('logout/',account.logout, name='logout'),
    path('image/code/',account.image_code, name='image_code'),
    # 首页
    path('index/',home.index,name='index'),
    # 项目列表
    path('project/list/',project.project_list,name='project_list'),
    path('project/star/<str:project_type>/<int:project_id>/',project.project_star,name='project_star'),
    path('project/unstar/<str:project_type>/<int:project_id>/',project.project_unstar,name='project_unstar'),
]