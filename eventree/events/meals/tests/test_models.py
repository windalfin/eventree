from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from eventree.events.models import Event
from eventree.events.meals.models import Meal, MealSelection
from eventree.events.registrations.models import Registration

User = get_user_model()

class MealModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Event Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Test Location',
            capacity=50,
            is_active=True
        )
        self.meal = Meal.objects.create(
            name='Test Meal',
            description='Test Description',
            event=self.event,
            available_quantity=10,
            meal_type='LUNCH',
            dietary_restriction='REGULAR',
            is_active=True
        )
        
        # Create users and registrations
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        self.registration1 = Registration.objects.create(
            user=self.user1,
            event=self.event
        )
        self.registration2 = Registration.objects.create(
            user=self.user2,
            event=self.event
        )

    def test_meal_str(self):
        expected = f"Test Meal (Lunch) - Regular"
        self.assertEqual(str(self.meal), expected)

    def test_meal_is_available(self):
        self.assertTrue(self.meal.is_available())
        
        # Create meal selections that consume all available quantity
        MealSelection.objects.create(
            registration=self.registration1,
            meal=self.meal,
            quantity=10
        )
        
        self.assertFalse(self.meal.is_available())

    def test_meal_remaining_quantity(self):
        self.assertEqual(self.meal.remaining_quantity(), 10)
        
        # Create meal selection
        MealSelection.objects.create(
            registration=self.registration1,
            meal=self.meal,
            quantity=3
        )
        
        self.assertEqual(self.meal.remaining_quantity(), 7)

    def test_meal_selections_count(self):
        self.assertEqual(self.meal.meal_selections.count(), 0)
        
        # Create meal selections
        MealSelection.objects.create(
            registration=self.registration1,
            meal=self.meal,
            quantity=2
        )
        MealSelection.objects.create(
            registration=self.registration2,
            meal=self.meal,
            quantity=3
        )
        
        self.assertEqual(self.meal.meal_selections.count(), 2)

class MealSelectionModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Event Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Test Location',
            capacity=50,
            is_active=True
        )
        self.meal = Meal.objects.create(
            name='Test Meal',
            description='Test Description',
            event=self.event,
            available_quantity=10,
            meal_type='LUNCH',
            dietary_restriction='REGULAR',
            is_active=True
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.registration = Registration.objects.create(
            user=self.user,
            event=self.event
        )

    def test_meal_selection_str(self):
        meal_selection = MealSelection.objects.create(
            registration=self.registration,
            meal=self.meal,
            quantity=2
        )
        expected = f"{self.registration.user.username}'s selection of {self.meal.name}"

        self.assertEqual(str(meal_selection), expected)

    def test_meal_selection_clean(self):
        # Test valid quantity
        meal_selection = MealSelection.objects.create(
            registration=self.registration,
            meal=self.meal,
            quantity=5
        )
        meal_selection.clean()  # Should not raise any exception
        
        # Test exceeding available quantity
        with self.assertRaises(ValueError):
            MealSelection.objects.create(
                registration=self.registration,
                meal=self.meal,
                quantity=11
            )

    def test_meal_selection_save(self):
        # Test saving with valid quantity
        meal_selection = MealSelection.objects.create(
            registration=self.registration,
            meal=self.meal,
            quantity=3
        )
        self.assertEqual(meal_selection.quantity, 3)
        
        # Test updating quantity
        meal_selection.quantity = 5
        meal_selection.save()
        meal_selection.refresh_from_db()
        self.assertEqual(meal_selection.quantity, 5)
