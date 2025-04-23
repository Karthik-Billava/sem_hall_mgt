from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking
from notifications.signals import notify

class Command(BaseCommand):
    help = 'Cancels bookings that have not been paid within 24 hours of approval'

    def handle(self, *args, **options):
        # Get approved bookings with approval_time set
        bookings = Booking.objects.filter(
            status='approved',
            approval_time__isnull=False
        )
        
        now = timezone.now()
        cancelled_count = 0
        
        for booking in bookings:
            # Skip if payment exists
            try:
                if booking.payment and booking.payment.status == 'completed':
                    continue
            except:
                pass
            
            # Check if deadline passed
            if booking.is_payment_deadline_passed():
                booking.status = 'cancelled'
                booking.save()
                cancelled_count += 1
                
                # Notify user about cancellation
                notify.send(
                    booking.venue.manager,
                    recipient=booking.user,
                    verb='cancelled your booking for',
                    target=booking.venue,
                    action_object=booking,
                    description=f"Your booking for {booking.venue.name} on {booking.date} has been automatically cancelled due to payment not being completed within 24 hours."
                )
                
                # Notify venue manager
                notify.send(
                    booking.user,
                    recipient=booking.venue.manager,
                    verb='had booking cancelled for',
                    target=booking.venue,
                    action_object=booking,
                    description=f"Booking for {booking.venue.name} on {booking.date} by {booking.user.username} was automatically cancelled due to non-payment."
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Cancelled booking {booking.id} - {booking.event_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cancelled {cancelled_count} unpaid bookings')
        ) 