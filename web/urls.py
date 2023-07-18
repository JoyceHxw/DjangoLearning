from django.urls import path
from web.views import account

urlpatterns = [
    path('register/',account.register, name='register'),
]