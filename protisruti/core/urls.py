from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('login-options/', views.login_options, name='login_options'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/counselor/', views.register_counselor,
         name='register_counselor'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/counselor/', views.counselor_dashboard,
         name='counselor_dashboard'),

    path('counselor/availability/', views.manage_availability,
         name='manage_availability'),
    path('counselor/availability/delete/<int:availability_id>/',
         views.delete_availability, name='delete_availability'),
    path('counselor/assignments/', views.view_assignments, name='view_assignments'),
    path('counselor/assignment/<int:assignment_id>/',
         views.assignment_detail, name='assignment_detail'),
    path('counselor/schedule-session/<int:assignment_id>/',
         views.schedule_session, name='schedule_session'),
    path('counselor/session/update-status/<int:session_id>/',
         views.update_session_status, name='update_session_status'),

    # Admin URLs for counselor verification and assignment
    path('admin/verify-counselors/',
         views.verify_counselors, name='verify_counselors'),
    path('admin/verify-counselor/<int:counselor_id>/',
         views.counselor_verification_detail, name='counselor_verification_detail'),
    path('admin/assign-counselor/',
         views.assign_counselor, name='assign_counselor'),

    path('victim/assignments/', views.victim_assignments,
         name='victim_assignments'),
    path('counselor/assignments/', views.counselor_assignments,
         name='counselor_assignments'),
]
