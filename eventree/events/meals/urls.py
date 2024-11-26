from django.urls import path
from . import views

app_name = 'meals'

urlpatterns = [
    # Meal URLs
    path('', views.MealListView.as_view(), name='meal_list'),
    path('<int:pk>/', views.MealDetailView.as_view(), name='meal_detail'),
    
    # Meal Selection URLs
    path('select/<int:registration_id>/', views.MealSelectionView.as_view(), name='meal_selection'),
    path('selections/', views.MealSelectionListView.as_view(), name='meal_selection_list'),
    path('selections/<int:pk>/', views.MealSelectionDetailView.as_view(), name='meal_selection_detail'),
    path('selections/<int:pk>/update/', views.MealSelectionUpdateView.as_view(), name='meal_selection_update'),
    
    # API endpoints for meal availability
    path('<int:pk>/availability/', views.MealAvailabilityView.as_view(), name='meal_availability'),
]
