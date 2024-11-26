from django.core.management.base import BaseCommand
from django.db import transaction
from eventree.events.models import Event
from eventree.events.meals.models import Meal
import random

class Command(BaseCommand):
    help = 'Populate the meals database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event',
            type=int,
            help='Event ID to create meals for. If not provided, creates meals for all events.'
        )

    def get_sample_meals(self):
        return {
            'BREAKFAST': [
                {
                    'name': 'Continental Breakfast',
                    'description': 'Fresh pastries, fruits, yogurt, and coffee',
                    'dietary_restriction': 'REGULAR',
                    'available_quantity': random.randint(20, 50)
                },
                {
                    'name': 'Vegan Breakfast Bowl',
                    'description': 'Quinoa, avocado, roasted vegetables, and tofu scramble',
                    'dietary_restriction': 'VEGAN',
                    'available_quantity': random.randint(10, 30)
                },
                {
                    'name': 'Gluten-Free Pancakes',
                    'description': 'Served with maple syrup and fresh berries',
                    'dietary_restriction': 'GLUTEN_FREE',
                    'available_quantity': random.randint(15, 40)
                }
            ],
            'LUNCH': [
                {
                    'name': 'Grilled Chicken Caesar Salad',
                    'description': 'Romaine lettuce, grilled chicken, parmesan, and caesar dressing',
                    'dietary_restriction': 'REGULAR',
                    'available_quantity': random.randint(20, 50)
                },
                {
                    'name': 'Vegetarian Buddha Bowl',
                    'description': 'Brown rice, roasted vegetables, chickpeas, and tahini dressing',
                    'dietary_restriction': 'VEGETARIAN',
                    'available_quantity': random.randint(15, 40)
                },
                {
                    'name': 'Halal Chicken Wrap',
                    'description': 'Halal chicken, lettuce, tomatoes, and hummus in a wrap',
                    'dietary_restriction': 'HALAL',
                    'available_quantity': random.randint(15, 35)
                }
            ],
            'DINNER': [
                {
                    'name': 'Grilled Salmon',
                    'description': 'Atlantic salmon with roasted vegetables and quinoa',
                    'dietary_restriction': 'REGULAR',
                    'available_quantity': random.randint(20, 50)
                },
                {
                    'name': 'Kosher Brisket',
                    'description': 'Slow-cooked brisket with roasted potatoes and vegetables',
                    'dietary_restriction': 'KOSHER',
                    'available_quantity': random.randint(15, 35)
                },
                {
                    'name': 'Vegan Pasta Primavera',
                    'description': 'Gluten-free pasta with seasonal vegetables and dairy-free sauce',
                    'dietary_restriction': 'VEGAN',
                    'available_quantity': random.randint(15, 40)
                }
            ],
            'SNACK': [
                {
                    'name': 'Fresh Fruit Platter',
                    'description': 'Assorted seasonal fruits',
                    'dietary_restriction': 'REGULAR',
                    'available_quantity': random.randint(30, 60)
                },
                {
                    'name': 'Gluten-Free Energy Bites',
                    'description': 'Made with dates, nuts, and dark chocolate',
                    'dietary_restriction': 'GLUTEN_FREE',
                    'available_quantity': random.randint(25, 50)
                },
                {
                    'name': 'Dairy-Free Smoothie',
                    'description': 'Blend of fruits, almond milk, and plant-based protein',
                    'dietary_restriction': 'DAIRY_FREE',
                    'available_quantity': random.randint(20, 45)
                }
            ]
        }

    @transaction.atomic
    def handle(self, *args, **options):
        event_id = options.get('event')
        
        if event_id:
            events = Event.objects.filter(id=event_id)
            if not events.exists():
                self.stdout.write(self.style.ERROR(f'Event with ID {event_id} does not exist'))
                return
        else:
            events = Event.objects.all()
            if not events.exists():
                self.stdout.write(self.style.ERROR('No events found in the database'))
                return

        sample_meals = self.get_sample_meals()
        meals_created = 0

        for event in events:
            self.stdout.write(f'Creating meals for event: {event.title}')
            
            for meal_type, meals in sample_meals.items():
                for meal_data in meals:
                    # Skip if meal with same name already exists for this event
                    if not Meal.objects.filter(event=event, name=meal_data['name']).exists():
                        Meal.objects.create(
                            event=event,
                            meal_type=meal_type,
                            **meal_data
                        )
                        meals_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {meals_created} meals for {events.count()} event(s)'
            )
        )
