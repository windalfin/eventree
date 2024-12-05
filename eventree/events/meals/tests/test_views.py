from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from eventree.events.models import Event
from eventree.events.meals.models import Meal, MealSelection
from eventree.events.registrations.models import Registration
from django.utils import timezone

User = get_user_model()

class MealViewsTest(TestCase):
    def setUp(self):
        # Create test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        # Create test event
        self.event = Event.objects.create(
            title='Test Event',
            description='Test Event Description',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=1),
            location='Test Location',
            capacity=50,
            is_active=True
        )
        
        # Create test meal
        self.meal = Meal.objects.create(
            name='Test Meal',
            description='Test Description',
            event=self.event,
            available_quantity=10,
            meal_type='LUNCH',
            dietary_restriction='REGULAR',
            is_active=True
        )
        
        # Create test registration
        self.registration = Registration.objects.create(
            user=self.user,
            event=self.event
        )

    def test_meal_list_view(self):
        # Test unauthenticated access
        response = self.client.get(reverse('events:meals:meal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Meal')
        
        # Test staff view
        self.client.login(username='staffuser', password='staffpass123')
        response = self.client.get(reverse('events:meals:meal_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Meal')
        
        # Test event filter
        response = self.client.get(f"{reverse('events:meals:meal_list')}?event={self.event.id}")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Meal')

    def test_meal_detail_view(self):
        url = reverse('events:meals:meal_detail', kwargs={'pk': self.meal.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Meal')
        self.assertContains(response, 'Test Description')

    def test_meal_selection_view(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('events:meals:meal_selection', 
                     kwargs={'registration_id': self.registration.pk})
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'meal': self.meal.pk,
            'quantity': 1
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(MealSelection.objects.filter(
            registration=self.registration,
            meal=self.meal
        ).exists())

    def test_meal_selection_update_view(self):
        self.client.login(username='testuser', password='testpass123')
        meal_selection = MealSelection.objects.create(
            registration=self.registration,
            meal=self.meal,
            quantity=1
        )
        
        url = reverse('events:meals:meal_selection_update', 
                     kwargs={'pk': meal_selection.pk})
        
        # Test GET request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test POST request
        data = {
            'meal': self.meal.pk,
            'quantity': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertRedirects(response, 
            reverse('events:registrations:registration_detail', 
                   kwargs={'pk': self.registration.pk}))
        meal_selection.refresh_from_db()
        self.assertEqual(meal_selection.quantity, 2)

    def test_meal_availability_view(self):
        url = reverse('events:meals:meal_availability', kwargs={'pk': self.meal.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('is_available', data)
        self.assertIn('remaining_quantity', data)

    def test_unauthorized_meal_selection_access(self):
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to create meal selection for another user's registration
        url = reverse('events:meals:meal_selection', 
                     kwargs={'registration_id': self.registration.pk})
        response = self.client.post(url, {
            'meal': self.meal.pk,
            'quantity': 1
        })
        self.assertEqual(response.status_code, 302)  # Redirects with error message
        self.assertFalse(MealSelection.objects.filter(
            registration=self.registration,
            meal=self.meal
        ).exists())
