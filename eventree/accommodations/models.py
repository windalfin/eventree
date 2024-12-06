from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

from eventree.events.models import Event

User = get_user_model()

class AccommodationType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Accommodation Type"
        verbose_name_plural = "Accommodation Types"

class Accommodation(models.Model):
    name = models.CharField(max_length=200)
    banner_image = models.ImageField(upload_to='accommodation_thumbnails/', blank=True, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    accommodation_type = models.ForeignKey(AccommodationType, on_delete=models.CASCADE, related_name='accommodations')
    address = models.CharField(max_length=355)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    description = models.TextField(blank=True)
    check_in_area = models.CharField(max_length=250, blank=True)  # e.g., "JUNIOR BALLROOM 1, 3rd Floor"
    hospitality_desk_location = models.CharField(max_length=200, blank=True)  # e.g., "Lobby Area"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Accommodation"
        verbose_name_plural = "Accommodations"

class AccommodationInstructions(models.Model):
    accommodation = models.OneToOneField(Accommodation, on_delete=models.CASCADE, related_name='instructions')
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    breakfast_included = models.BooleanField(default=False)
    breakfast_time = models.TimeField(null=True, blank=True)
    breakfast_location = models.CharField(max_length=200, blank=True)  # e.g., "The Stone Kitchen Restaurant"
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Instructions for {self.accommodation.name}"

    class Meta:
        verbose_name = "Accommodation Instructions"
        verbose_name_plural = "Accommodation Instructions"

class ShuttleService(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name='shuttle_services')
    service_name = models.CharField(max_length=200)
    pickup_location = models.CharField(max_length=255)
    destination = models.ForeignKey(
        Accommodation, 
        on_delete=models.CASCADE, 
        related_name='destination_shuttles',
        null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_name} - {self.accommodation.name}"

    class Meta:
        verbose_name = "Shuttle Service"
        verbose_name_plural = "Shuttle Services"

class ShuttleSchedule(models.Model):
    shuttle_service = models.ForeignKey(ShuttleService, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    scheduled_date = models.DateField()
    capacity = models.IntegerField(default=10)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shuttle_service.service_name} - {self.scheduled_date} {self.departure_time}"

    class Meta:
        verbose_name = "Shuttle Schedule"
        verbose_name_plural = "Shuttle Schedules"
        ordering = ['scheduled_date', 'departure_time']

class ParticipantAccommodation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField()
    room_number = models.CharField(max_length=50, blank=True)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.accommodation.name}"

    class Meta:
        verbose_name = "Participant Accommodation"
        verbose_name_plural = "Participant Accommodations"
        unique_together = ['user', 'event']