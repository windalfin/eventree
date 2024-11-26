from django.db import models
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def is_past_event(self):
        return self.end_date < timezone.now()

    def is_full(self):
        from .registrations.models import Registration
        return Registration.objects.filter(event=self).count() >= self.capacity

    def available_spots(self):
        from .registrations.models import Registration
        current_registrations = Registration.objects.filter(event=self).count()
        return max(0, self.capacity - current_registrations)

    def get_event_date_string(self):
        if self.start_date.date() == self.end_date.date():
            return self.start_date.strftime('%B %d, %Y')
        return f"{self.start_date.strftime('%B %d, %Y')} - {self.end_date.strftime('%B %d, %Y')}"

    def get_event_time_string(self):
        if self.start_date.date() == self.end_date.date():
            return self.start_date.strftime('%I:%M %p')
        return f"{self.start_date.strftime('%I:%M %p')} - {self.end_date.strftime('%I:%M %p')}"
        
    @property
    def is_available(self):
        """
        Check if the event is available for registration.
        An event is available if:
        1. It is active
        2. It hasn't ended
        3. It has available spots
        """
        return (
            self.is_active and
            not self.is_past_event() and
            not self.is_full()
        )