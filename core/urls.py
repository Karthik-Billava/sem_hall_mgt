from django.urls import path,include
from . import views

app_name = 'corehome56'

urlpatterns = [
    path('',views.home,name="home",),
]
