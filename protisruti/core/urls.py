from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('login-options/', views.login_options, name='login_options'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/counselor/', views.register_counselor, name='register_counselor'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/counselor/', views.counselor_dashboard, name='counselor_dashboard'),
]