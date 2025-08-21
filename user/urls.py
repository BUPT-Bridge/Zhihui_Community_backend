from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # 微信登录接口
    path('wx-login/', views.WxLoginView.as_view(), name='wx_login'),
    
    # 用户资料接口
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
]
