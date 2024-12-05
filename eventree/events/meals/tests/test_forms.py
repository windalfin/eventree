from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from eventree.events.models import Event
from eventree.events.meals.models import Meal, MealSelection
from eventree.events.registrations.models import Registration
from eventree.events.meals.forms import MealSelectionForm

User = get_user_model()

class MealSelectionFormTest(TestCase):
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

    def test_valid_form(self):
        form_data = {
            'meal': self.meal.id,
            'quantity': 5
        }
        form = MealSelectionForm(data=form_data, registration=self.registration)
        self.assertTrue(form.is_valid())

    def test_invalid_quantity(self):
        # Test quantity exceeding available meals
        form_data = {
            'meal': self.meal.id,
            'quantity': 11
        }
        form = MealSelectionForm(data=form_data, registration=self.registration)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('servings of this meal are available', form.errors['__all__'][0])

    def test_negative_quantity(self):
        form_data = {
            'meal': self.meal.id,
            'quantity': -1
        }
        form = MealSelectionForm(data=form_data, registration=self.registration)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertIn('Quantity must be at least 1', form.errors['quantity'][0])

    def test_zero_quantity(self):
        form_data = {
            'meal': self.meal.id,
            'quantity': 0
        }
        form = MealSelectionForm(data=form_data, registration=self.registration)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertIn('Quantity must be at least 1', form.errors['quantity'][0])

    def test_meal_from_different_event(self):
        # Create meal from different event
        other_event = Event.objects.create(
            title='Other Event',
            description='Other Event Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Other Location',
            capacity=50,
            is_active=True
        )
        other_meal = Meal.objects.create(
            name='Other Meal',
            description='Other Description',
            event=other_event,
            available_quantity=10,
            meal_type='DINNER',
            dietary_restriction='REGULAR',
            is_active=True
        )
        
        form_data = {
            'meal': other_meal.id,
            'quantity': 1
        }
        form = MealSelectionForm(data=form_data, registration=self.registration)
        self.assertFalse(form.is_valid())
        self.assertIn('meal', form.errors)

    def test_inactive_meal(self):
        self.meal.is_active = False
        self.meal.save()
        
        form_data = {
            'meal': self.meal.id,
            'quantity': 1
        }
        form = MealSelectionForm(data=form_data, registration=self.registration)
        self.assertFalse(form.is_valid())
        self.assertIn('meal', form.errors)

    def test_meal_queryset(self):
        # Create another meal in the same event
        other_meal = Meal.objects.create(
            name='Other Meal',
            description='Other Description',
            event=self.event,
            available_quantity=5,
            meal_type='LUNCH',
            dietary_restriction='REGULAR',
            is_active=True
        )
        
        form = MealSelectionForm(registration=self.registration)
        queryset = form.fields['meal'].queryset
        
        # Check that only meals from the same event are available
        self.assertEqual(queryset.count(), 2)
        self.assertIn(self.meal, queryset)
        self.assertIn(other_meal, queryset)
