from django.urls import path, include
from . import views

app_name = 'events'

urlpatterns = [
    # Event URLs
    path('', views.EventListView.as_view(), name='event_list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('<int:pk>/register/', views.EventRegistrationView.as_view(), name='event_register'),
    
    # Include registration and meal URLs
    path('registrations/', include(('eventree.events.registrations.urls', 'events'), namespace='registrations')),
    path('meals/', include(('eventree.events.meals.urls', 'events'), namespace='meals')),

]
