from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404, JsonResponse
from .models import Meal, MealSelection
from ..models import Event
from ..registrations.models import Registration
from .forms import MealSelectionForm


class MealListView(ListView):
    model = Meal
    template_name = 'meals/meal_list.html'
    context_object_name = 'meals'

    def get_queryset(self):
        queryset = Meal.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        event_id = self.request.GET.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_id = self.request.GET.get('event')
        if event_id:
            context['event'] = get_object_or_404(Event, pk=event_id)
        return context


class MealDetailView(DetailView):
    model = Meal
    template_name = 'meals/meal_detail.html'
    context_object_name = 'meal'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_available'] = self.object.is_available()
        context['remaining_quantity'] = self.object.remaining_quantity()
        return context


class MealSelectionView(LoginRequiredMixin, CreateView):
    model = MealSelection
    template_name = 'meals/meal_selection_form.html'
    form_class = MealSelectionForm

    def get_success_url(self):
        return reverse_lazy('events:registrations:registration_detail', 
                          kwargs={'pk': self.kwargs['registration_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration'] = get_object_or_404(
            Registration, pk=self.kwargs['registration_id']
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        registration = get_object_or_404(Registration, pk=self.kwargs['registration_id'])
        kwargs['registration'] = registration
        return kwargs

    def form_valid(self, form):
        registration = get_object_or_404(
            Registration, pk=self.kwargs['registration_id']
        )
        if registration.user != self.request.user and not self.request.user.is_staff:
            messages.error(self.request, 'You can only select meals for your own registration.')
            return redirect('events:registrations:registration_detail', 
                          pk=registration.pk)
        
        form.instance.registration = registration
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Meal selection saved successfully!')
            return response
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class MealSelectionUpdateView(LoginRequiredMixin, UpdateView):
    model = MealSelection
    template_name = 'meals/meal_selection_form.html'
    form_class = MealSelectionForm

    def get_success_url(self):
        return reverse_lazy('events:registrations:registration_detail', 
                          kwargs={'pk': self.object.registration.pk})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.registration.user != self.request.user and not self.request.user.is_staff:
            raise Http404("Meal selection not found")
        return obj

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        registration = self.object.registration
        kwargs['registration'] = registration
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Meal selection updated successfully!')
            return response
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class MealSelectionDetailView(LoginRequiredMixin, DetailView):
    model = MealSelection
    template_name = 'meals/meal_selection_detail.html'
    context_object_name = 'meal_selection'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Only allow staff or the user who owns the registration to view
        if not self.request.user.is_staff and obj.registration.user != self.request.user:
            raise Http404("Meal selection not found")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = (
            self.request.user.is_staff or 
            self.object.registration.user == self.request.user
        )
        return context


class MealSelectionListView(LoginRequiredMixin, ListView):
    model = MealSelection
    template_name = 'meals/meal_selection_list.html'
    context_object_name = 'meal_selections'

    def get_queryset(self):
        if self.request.user.is_staff:
            return MealSelection.objects.all()
        return MealSelection.objects.filter(
            registration__user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group meal selections by registration
        selections_by_registration = {}
        for selection in self.get_queryset():
            if selection.registration_id not in selections_by_registration:
                selections_by_registration[selection.registration_id] = {
                    'registration': selection.registration,
                    'selections': []
                }
            selections_by_registration[selection.registration_id]['selections'].append(selection)
        context['selections_by_registration'] = selections_by_registration
        return context


class MealAvailabilityView(View):
    def get(self, request, *args, **kwargs):
        meal = get_object_or_404(Meal, pk=kwargs['pk'])
        return JsonResponse({
            'is_available': meal.is_available(),
            'remaining_quantity': meal.remaining_quantity(),
            'total_capacity': meal.quantity,
            'meal_name': meal.name,
            'meal_type': meal.meal_type,
            'dietary_info': meal.dietary_info
        })
