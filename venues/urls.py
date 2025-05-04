from django.urls import path
from . import views

urlpatterns = [
    path('', views.venue_list, name='venue_list'),
    path('<int:venue_id>/', views.venue_detail, name='venue_detail'),
    path('manage/', views.manage_venues, name='manage_venues'),
    path('add/', views.add_venue, name='add_venue'),
    path('edit/<int:venue_id>/', views.edit_venue, name='edit_venue'),
    path('delete/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('images/<int:venue_id>/', views.manage_venue_images, name='manage_venue_images'),
    path('images/delete/<int:image_id>/', views.delete_venue_image, name='delete_venue_image'),
    path('images/set-primary/<int:image_id>/', views.set_primary_image, name='set_primary_image'),
    path('images/set-cover/<int:image_id>/', views.set_cover_image, name='set_cover_image'),
    path('bookings/<int:venue_id>/', views.venue_bookings, name='venue_bookings'),
] 