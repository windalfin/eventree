from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

from eventree.events.models import Event
from eventree.events.registrations.models import Registration, Invitation

User = get_user_model()

class RegistrationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Test Location',
            capacity=100
        )
        
        self.registration = Registration.objects.create(
            user=self.user,
            event=self.event,
            status='PENDING'
        )

    def test_registration_creation(self):
        """Test registration is created with correct default values"""
        self.assertEqual(self.registration.status, 'PENDING')
        self.assertFalse(self.registration.is_verified)
        self.assertIsNone(self.registration.invited_by)

    def test_registration_str_method(self):
        """Test the string representation of Registration"""
        expected_str = f"{self.user.username}'s Registration for {self.event.title}"
        self.assertEqual(str(self.registration), expected_str)

    def test_registration_status_changes(self):
        """Test status change methods"""
        self.registration.confirm()
        self.assertEqual(self.registration.status, 'CONFIRMED')
        
        self.registration.cancel()
        self.assertEqual(self.registration.status, 'CANCELLED')

    def test_duplicate_registration_prevention(self):
        """Test that a user cannot register twice for the same event"""
        with self.assertRaises(ValidationError):
            duplicate_reg = Registration(
                user=self.user,
                event=self.event,
                status='PENDING'
            )
            duplicate_reg.full_clean()

class InvitationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Test Location',
            capacity=100
        )
        
        self.registration = Registration.objects.create(
            user=self.user,
            event=self.event,
            status='CONFIRMED'
        )

    def test_invitation_creation(self):
        """Test invitation is created with correct default values"""
        invitation = Invitation.objects.create(
            registration=self.registration,
            email='guest@example.com',
            invitation_type='GUEST'
        )
        
        self.assertEqual(invitation.status, 'PENDING')
        self.assertIsNotNone(invitation.token)
        self.assertIsNotNone(invitation.expires_at)
        
    def test_invitation_expiration(self):
        """Test invitation expiration"""
        invitation = Invitation.objects.create(
            registration=self.registration,
            email='guest@example.com',
            invitation_type='GUEST',
            expires_at=timezone.now() - timezone.timedelta(days=1)
        )
        
        # Try to accept an expired invitation
        new_user = User.objects.create_user(
            username='newuser',
            email='guest@example.com',
            password='testpass123'
        )
        
        with self.assertRaises(ValueError):
            invitation.accept(new_user)
            
        self.assertEqual(invitation.status, 'EXPIRED')

    def test_invitation_accept(self):
        """Test accepting an invitation creates a new registration"""
        invitation = Invitation.objects.create(
            registration=self.registration,
            email='guest@example.com',
            invitation_type='GUEST'
        )
        
        new_user = User.objects.create_user(
            username='newuser',
            email='guest@example.com',
            password='testpass123'
        )
        
        invitation.accept(new_user)
        
        # Check that a new registration was created
        new_registration = Registration.objects.filter(
            user=new_user,
            event=self.event
        ).first()
        
        self.assertIsNotNone(new_registration)
        self.assertEqual(invitation.status, 'ACCEPTED')
