from django.urls import path
from . import views

urlpatterns = [
    path('venue/<int:venue_id>/', views.book_venue, name='book_venue'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('approve/<int:booking_id>/', views.approve_booking, name='approve_booking'),
    path('reject/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('payment/<int:booking_id>/', views.make_payment, name='make_payment'),
    path('check-availability/<int:venue_id>/', views.check_availability, name='check_availability'),
] 