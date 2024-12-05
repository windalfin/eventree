from django.db import models
from django.core.validators import MinValueValidator
from ..models import Event
from ..registrations.models import Registration

class Meal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('DINNER', 'Dinner'),
        ('SNACK', 'Snack'),
    ]

    DIETARY_RESTRICTION_CHOICES = [
        ('REGULAR', 'Regular'),
        ('VEGETARIAN', 'Vegetarian'),
        ('VEGAN', 'Vegan'),
        ('HALAL', 'Halal'),
        ('KOSHER', 'Kosher'),
        ('GLUTEN_FREE', 'Gluten Free'),
        ('DAIRY_FREE', 'Dairy Free'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='meals')
    name = models.CharField(max_length=200)
    description = models.TextField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    dietary_restriction = models.CharField(
        max_length=20, 
        choices=DIETARY_RESTRICTION_CHOICES,
        default='REGULAR'
    )
    available_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['meal_type', 'name']
        unique_together = ['event', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_meal_type_display()}) - {self.get_dietary_restriction_display()}"

    def is_available(self):
        """Check if meal is still available"""
        total_selected = self.meal_selections.aggregate(
            total=models.Sum('quantity'))['total'] or 0
        return self.is_active and self.available_quantity > total_selected

    def remaining_quantity(self):
        """Get remaining available quantity"""
        total_selected = self.meal_selections.aggregate(
            total=models.Sum('quantity'))['total'] or 0
        return max(0, self.available_quantity - total_selected)


class MealSelection(models.Model):
    registration = models.ForeignKey(
        Registration, 
        on_delete=models.CASCADE,
        related_name='meal_selections'
    )
    meal = models.ForeignKey(
        Meal, 
        on_delete=models.CASCADE,
        related_name='meal_selections'
    )
    quantity = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['registration', 'meal']
        verbose_name = 'Meal Selection'
        verbose_name_plural = 'Meal Selections'

    def __str__(self):
        return f"{self.registration.user.username}'s selection of {self.meal.name}"

    def save(self, *args, **kwargs):
        # Check if there's enough quantity available
        current_selections = self.meal.meal_selections.exclude(id=self.id).aggregate(
            total=models.Sum('quantity'))['total'] or 0
        if current_selections + self.quantity > self.meal.available_quantity:
            raise ValueError("Not enough meals available")
        super().save(*args, **kwargs)
