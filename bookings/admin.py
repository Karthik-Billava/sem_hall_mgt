from django.contrib import admin
from .models import Booking, Payment

class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    extra = 0

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'event_name', 'venue', 'user', 'date', 'status', 'total_cost')
    list_filter = ('status', 'date')
    search_fields = ('booking_id', 'event_name', 'user__username', 'venue__name')
    readonly_fields = ('booking_id', 'created_at', 'updated_at')
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'status', 'payment_date')
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('booking__booking_id', 'transaction_id')
    readonly_fields = ('payment_date',) 