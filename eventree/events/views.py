from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Event
from .forms import EventRegistrationForm


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        queryset = Event.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_registration'] = self.object.registrations.filter(
                user=self.request.user
            ).first()
        return context


class EventRegistrationView(LoginRequiredMixin, CreateView):
    template_name = 'events/registration_form.html'
    form_class = EventRegistrationForm
    success_url = reverse_lazy('events:event_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        if not event.is_available:
            messages.error(self.request, 'Sorry, this event is full.')
            return redirect('events:event_detail', pk=event.pk)
        
        form.instance.event = event
        form.instance.user = self.request.user
        messages.success(self.request, 'Successfully registered for the event!')
        return super().form_valid(form)
