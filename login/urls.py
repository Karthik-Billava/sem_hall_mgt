# auth/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
    path('dashboard/regular/<slug:slug>', views.regular_dashboard, name="regular_dashboard"),
    path('dashboard/manager/<slug:slug>', views.manager_dashboard, name="manager_dashboard"),
]
