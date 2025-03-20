from django.urls import path, include
from . import views

app_name = 'corehome56'

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/regular/', views.regular_dashboard, name="regular_dashboard"),
    path('dashboard/manager/', views.manager_dashboard, name="manager_dashboard"),
]
