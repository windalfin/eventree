from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import time, date
from eventree.accommodations.models import (
    AccommodationType, Accommodation, AccommodationInstructions,
    ShuttleService, ShuttleSchedule, ParticipantAccommodation
)
from eventree.events.models import Event

User = get_user_model()

class AccommodationTypeTests(TestCase):
    def setUp(self):
        self.acc_type = AccommodationType.objects.create(
            name="Hotel",
            description="Luxury hotel accommodation"
        )

    def test_accommodation_type_creation(self):
        self.assertEqual(self.acc_type.name, "Hotel")
        self.assertEqual(self.acc_type.description, "Luxury hotel accommodation")
        self.assertTrue(isinstance(self.acc_type, AccommodationType))
        self.assertEqual(str(self.acc_type), "Hotel")

    def test_accommodation_type_name_max_length(self):
        acc_type = AccommodationType(name="H" * 101)  # Max length is 100
        with self.assertRaises(ValidationError):
            acc_type.full_clean()

class AccommodationTests(TestCase):
    def setUp(self):
        self.acc_type = AccommodationType.objects.create(name="Hotel")
        self.accommodation = Accommodation.objects.create(
            name="Grand Hotel",
            accommodation_type=self.acc_type,
            address="123 Main St",
            latitude=40.7128,
            longitude=-74.0060
        )

    def test_accommodation_creation(self):
        self.assertEqual(self.accommodation.name, "Grand Hotel")
        self.assertEqual(self.accommodation.accommodation_type, self.acc_type)
        self.assertEqual(self.accommodation.address, "123 Main St")
        self.assertEqual(float(self.accommodation.latitude), 40.7128)
        self.assertEqual(float(self.accommodation.longitude), -74.0060)
        self.assertEqual(str(self.accommodation), "Grand Hotel")

    def test_accommodation_type_relationship(self):
        self.assertEqual(self.acc_type.accommodations.first(), self.accommodation)

class AccommodationInstructionsTests(TestCase):
    def setUp(self):
        self.acc_type = AccommodationType.objects.create(name="Hotel")
        self.accommodation = Accommodation.objects.create(
            name="Grand Hotel",
            accommodation_type=self.acc_type,
            address="123 Main St"
        )
        self.instructions = AccommodationInstructions.objects.create(
            accommodation=self.accommodation,
            check_in_time=time(14, 0),  # 2:00 PM
            check_out_time=time(11, 0),  # 11:00 AM
            breakfast_included=True,
            breakfast_time=time(7, 0),  # 7:00 AM
            special_instructions="Please call 30 minutes before arrival"
        )

    def test_instructions_creation(self):
        self.assertEqual(self.instructions.accommodation, self.accommodation)
        self.assertEqual(self.instructions.check_in_time, time(14, 0))
        self.assertEqual(self.instructions.check_out_time, time(11, 0))
        self.assertTrue(self.instructions.breakfast_included)
        self.assertEqual(self.instructions.breakfast_time, time(7, 0))
        self.assertEqual(
            str(self.instructions),
            f"Instructions for {self.accommodation.name}"
        )

    def test_one_to_one_relationship(self):
        # Test that we can't create multiple instructions for same accommodation
        with self.assertRaises(IntegrityError):
            AccommodationInstructions.objects.create(
                accommodation=self.accommodation,
                check_in_time=time(15, 0),
                check_out_time=time(10, 0)
            )

class ShuttleServiceTests(TestCase):
    def setUp(self):
        self.acc_type = AccommodationType.objects.create(name="Hotel")
        self.accommodation = Accommodation.objects.create(
            name="Grand Hotel",
            accommodation_type=self.acc_type,
            address="123 Main St"
        )
        self.destination = Accommodation.objects.create(
            name="Airport",
            accommodation_type=self.acc_type,
            address="Airport Road 1"
        )
        self.shuttle = ShuttleService.objects.create(
            accommodation=self.accommodation,
            service_name="Airport Shuttle",
            pickup_location="Hotel Lobby",
            destination=self.destination,
            is_active=True
        )

    def test_shuttle_service_creation(self):
        self.assertEqual(self.shuttle.accommodation, self.accommodation)
        self.assertEqual(self.shuttle.service_name, "Airport Shuttle")
        self.assertEqual(self.shuttle.pickup_location, "Hotel Lobby")
        self.assertEqual(self.shuttle.destination, self.destination)
        self.assertTrue(self.shuttle.is_active)
        self.assertEqual(
            str(self.shuttle),
            f"Airport Shuttle - {self.accommodation.name}"
        )

    def test_multiple_shuttle_services(self):
        # Test that we can create multiple shuttle services for one accommodation
        city_shuttle = ShuttleService.objects.create(
            accommodation=self.accommodation,
            service_name="City Center Shuttle",
            pickup_location="Hotel Lobby",
            destination=self.destination,
            is_active=True
        )
        self.assertEqual(self.accommodation.shuttle_services.count(), 2)

class ShuttleScheduleTests(TestCase):
    def setUp(self):
        self.acc_type = AccommodationType.objects.create(name="Hotel")
        self.accommodation = Accommodation.objects.create(
            name="Grand Hotel",
            accommodation_type=self.acc_type,
            address="123 Main St"
        )
        self.destination = Accommodation.objects.create(
            name="Airport",
            accommodation_type=self.acc_type,
            address="Airport Road 1"
        )
        self.shuttle = ShuttleService.objects.create(
            accommodation=self.accommodation,
            service_name="Airport Shuttle",
            pickup_location="Hotel Lobby",
            destination=self.destination,
            is_active=True
        )
        self.schedule = ShuttleSchedule.objects.create(
            shuttle_service=self.shuttle,
            departure_time=time(14, 0),  # 2:00 PM
            scheduled_date=date(2024, 1, 1),
            capacity=10,
            notes="Regular service",
            is_active=True
        )

    def test_shuttle_schedule_creation(self):
        self.assertEqual(self.schedule.shuttle_service, self.shuttle)
        self.assertEqual(self.schedule.departure_time, time(14, 0))
        self.assertEqual(self.schedule.scheduled_date, date(2024, 1, 1))
        self.assertEqual(self.schedule.capacity, 10)
        self.assertEqual(self.schedule.notes, "Regular service")
        self.assertTrue(self.schedule.is_active)
        self.assertEqual(
            str(self.schedule),
            f"Airport Shuttle - 2024-01-01 14:00:00"
        )

    def test_multiple_schedules(self):
        # Test that we can create multiple schedules for one shuttle service
        another_schedule = ShuttleSchedule.objects.create(
            shuttle_service=self.shuttle,
            departure_time=time(16, 0),  # 4:00 PM
            scheduled_date=date(2024, 1, 1),
            capacity=10,
            is_active=True
        )
        self.assertEqual(self.shuttle.schedules.count(), 2)

class ParticipantAccommodationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Event Description",
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location="Test Location",
            capacity=100,
            is_active=True
        )
        self.acc_type = AccommodationType.objects.create(name="Hotel")
        self.accommodation = Accommodation.objects.create(
            name="Grand Hotel",
            accommodation_type=self.acc_type,
            address="123 Main St"
        )
        self.participant_accommodation = ParticipantAccommodation.objects.create(
            user=self.user,
            event=self.event,
            accommodation=self.accommodation,
            check_in_time=timezone.now(),
            check_out_time=timezone.now() + timezone.timedelta(days=1),
            room_number="101",
            special_requests="Late check-out requested"
        )

    def test_participant_accommodation_creation(self):
        self.assertEqual(self.participant_accommodation.user, self.user)
        self.assertEqual(self.participant_accommodation.event, self.event)
        self.assertEqual(self.participant_accommodation.accommodation, self.accommodation)
        self.assertEqual(self.participant_accommodation.room_number, "101")
        self.assertEqual(
            self.participant_accommodation.special_requests,
            "Late check-out requested"
        )
        self.assertEqual(
            str(self.participant_accommodation),
            f"testuser - Grand Hotel"
        )

    def test_unique_together_constraint(self):
        # Test that we can't create multiple accommodations for same user and event
        with self.assertRaises(IntegrityError):
            ParticipantAccommodation.objects.create(
                user=self.user,
                event=self.event,
                accommodation=self.accommodation,
                check_in_time=timezone.now(),
                check_out_time=timezone.now() + timezone.timedelta(days=1)
            )
