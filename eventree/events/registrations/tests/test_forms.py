from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from eventree.events.models import Event
from eventree.events.registrations.models import Registration, Invitation
from eventree.events.registrations.forms import InviteGuestForm

User = get_user_model()

class InviteGuestFormTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
        # Create a test event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Test Location',
            capacity=100
        )
        
        # Create a registration for the test user
        self.registration = Registration.objects.create(
            user=self.user,
            event=self.event,
            status='CONFIRMED'
        )

    def test_invite_guest_form_valid_data(self):
        """Test form with valid email"""
        form = InviteGuestForm(
            data={'email': 'newguest@example.com'},
            registration=self.registration
        )
        self.assertTrue(form.is_valid())

    def test_invite_guest_form_invalid_email(self):
        """Test form with invalid email format"""
        form = InviteGuestForm(
            data={'email': 'invalid-email'},
            registration=self.registration
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_invite_guest_form_duplicate_email(self):
        """Test form with an email that's already registered for the event"""
        # Create another user and register them for the event
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        Registration.objects.create(
            user=other_user,
            event=self.event,
            status='CONFIRMED'
        )

        # Try to invite the already registered user
        form = InviteGuestForm(
            data={'email': 'other@example.com'},
            registration=self.registration
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already registered', str(form.errors['email']))
