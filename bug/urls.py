from django.urls import path
from bug import views

urlpatterns = [
    path('sms/code/',views.send_sms),
    path('register/',views.register,name='register'),
]