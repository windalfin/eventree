# Generated by Django 5.0.9 on 2024-11-26 08:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('registrations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('meal_type', models.CharField(choices=[('BREAKFAST', 'Breakfast'), ('LUNCH', 'Lunch'), ('DINNER', 'Dinner'), ('SNACK', 'Snack')], max_length=20)),
                ('dietary_restriction', models.CharField(choices=[('REGULAR', 'Regular'), ('VEGETARIAN', 'Vegetarian'), ('VEGAN', 'Vegan'), ('HALAL', 'Halal'), ('KOSHER', 'Kosher'), ('GLUTEN_FREE', 'Gluten Free'), ('DAIRY_FREE', 'Dairy Free')], default='REGULAR', max_length=20)),
                ('available_quantity', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meals', to='events.event')),
            ],
            options={
                'ordering': ['meal_type', 'name'],
                'unique_together': {('event', 'name')},
            },
        ),
        migrations.CreateModel(
            name='MealSelection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('special_requests', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_selections', to='meals.meal')),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_selections', to='registrations.registration')),
            ],
            options={
                'verbose_name': 'Meal Selection',
                'verbose_name_plural': 'Meal Selections',
                'unique_together': {('registration', 'meal')},
            },
        ),
    ]
