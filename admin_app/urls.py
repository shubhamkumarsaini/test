from django.urls import path
from .views import *

urlpatterns = [
    path('',admin_login,name='admin_login'),
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('admindashboard/',admindashboard_page,name='admindashboard'),
    # path('show_user/',show_user,name='show_user'),
    # path('add_user/',add_user,name='add_user'),
    # path('edit_user/<int:user_id>/', edit_user, name='edit_user'),
    # path('delete_user/<int:user_id>/', delete_user, name='delete_user'),
    # path('edit_about/<int:about_id>/', edit_about, name='edit_about'),
    # path('admin_profile/', admin_profile, name='admin_profile'), 
]
