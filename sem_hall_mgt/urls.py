"""
URL configuration for sem_hall_mgt project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve
from . import views  

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('venues/', include('venues.urls')),
    path('bookings/', include('bookings.urls')),
    path('notifications/', include('notifications_app.urls')),
    path('', views.home_view, name='home'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Serve user uploads from the configured persistent media directory.
    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]
