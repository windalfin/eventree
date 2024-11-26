from django.db import models
from django.utils import timezone
from django.conf import settings

from eventree.events.models import Event
import uuid

User = settings.AUTH_USER_MODEL

class Registration(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    phone_number = models.CharField(max_length=15, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    invited_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='invited_registrations')
    
    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'
        unique_together = ['user', 'event']  # Prevent duplicate registrations
    
    def __str__(self):
        return f"{self.user.username}'s Registration for {self.event.title}"
        
    def confirm(self):
        self.status = 'CONFIRMED'
        self.save()
        
    def cancel(self):
        self.status = 'CANCELLED'
        self.save()

    def invite_spouse(self, email):
        """
        Create an invitation for a spouse to join the event
        """
        invitation = Invitation.objects.create(
            registration=self,
            email=email,
            invitation_type='SPOUSE'
        )
        return invitation


class Invitation(models.Model):
    INVITATION_TYPES = [
        ('SPOUSE', 'Spouse'),
        ('FAMILY', 'Family Member'),
        ('GUEST', 'Guest'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('EXPIRED', 'Expired'),
    ]
    
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='sent_invitations')
    email = models.EmailField()
    invitation_type = models.CharField(max_length=10, choices=INVITATION_TYPES, default='GUEST')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.registration.event.title}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 7 days from creation by default
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    def accept(self, user):
        """
        Accept the invitation and create a registration for the invited user
        """
        if self.status != 'PENDING':
            raise ValueError("This invitation has already been processed")
            
        if timezone.now() > self.expires_at:
            self.status = 'EXPIRED'
            self.save()
            raise ValueError("This invitation has expired")
            
        # Create registration for the invited user
        registration = Registration.objects.create(
            user=user,
            event=self.registration.event,
            status='CONFIRMED',
            invited_by=self.registration
        )
        
        self.status = 'ACCEPTED'
        self.save()
        return registration
    
    def decline(self):
        """
        Decline the invitation
        """
        self.status = 'DECLINED'
        self.save()