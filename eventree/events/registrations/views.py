from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from .models import Registration, Invitation
from .forms import InviteGuestForm


class RegistrationListView(LoginRequiredMixin, ListView):
    model = Registration
    template_name = 'registrations/registration_list.html'
    context_object_name = 'registrations'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Registration.objects.all()
        return Registration.objects.filter(user=self.request.user)


class RegistrationDetailView(LoginRequiredMixin, DetailView):
    model = Registration
    template_name = 'registrations/registration_detail.html'
    context_object_name = 'registration'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_staff and obj.user != self.request.user:
            raise Http404("Registration not found")
        return obj


class InviteGuestView(LoginRequiredMixin, CreateView):
    template_name = 'registrations/invite_form.html'
    form_class = InviteGuestForm
    
    def get_success_url(self):
        return reverse_lazy('events:registrations:registration_detail', 
                          kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        registration = get_object_or_404(Registration, pk=self.kwargs['pk'])
        kwargs['registration'] = registration
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration'] = get_object_or_404(
            Registration, pk=self.kwargs['pk']
        )
        return context

    def form_valid(self, form):
        registration = get_object_or_404(Registration, pk=self.kwargs['pk'])
        if registration.user != self.request.user:
            messages.error(self.request, 'You can only invite guests to your own registration.')
            return redirect('events:registrations:registration_detail', pk=registration.pk)
        
        try:
            form.instance.registration = registration
            invitation = form.save()
            messages.success(self.request, f'Invitation sent to {invitation.email}')
            return super().form_valid(form)
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class InvitationListView(LoginRequiredMixin, ListView):
    model = Invitation
    template_name = 'registrations/invitation_list.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Invitation.objects.all()
        return Invitation.objects.filter(registration__user=self.request.user)


class InvitationDetailView(LoginRequiredMixin, DetailView):
    model = Invitation
    template_name = 'registrations/invitation_detail.html'
    context_object_name = 'invitation'
    slug_field = 'token'
    slug_url_kwarg = 'token'


class InvitationAcceptView(LoginRequiredMixin, UpdateView):
    model = Invitation
    template_name = 'registrations/invitation_accept.html'
    fields = []  # No fields needed, just confirmation
    slug_field = 'token'
    slug_url_kwarg = 'token'

    def form_valid(self, form):
        invitation = self.get_object()
        try:
            registration = invitation.accept(self.request.user)
            messages.success(self.request, 'Successfully accepted the invitation!')
            return redirect('events:registrations:registration_detail', pk=registration.pk)
        except ValueError as e:
            messages.error(self.request, str(e))
            return redirect('events:registrations:invitation_detail', token=invitation.token)


class InvitationDeclineView(LoginRequiredMixin, UpdateView):
    model = Invitation
    template_name = 'registrations/invitation_decline.html'
    fields = []  # No fields needed, just confirmation
    slug_field = 'token'
    slug_url_kwarg = 'token'

    def form_valid(self, form):
        invitation = self.get_object()
        invitation.decline()
        messages.success(self.request, 'Invitation declined.')
        return redirect('events:event_list')


class VerifyRegistrationView(TemplateView):
    template_name = 'registrations/verify_registration.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            registration = Registration.objects.get(verification_token=token)
            if not registration.is_verified:
                registration.verify()
                messages.success(request, 'Your registration has been verified!')
            else:
                messages.info(request, 'This registration was already verified.')
            return redirect('events:registrations:registration_detail', pk=registration.pk)
        except Registration.DoesNotExist:
            messages.error(request, 'Invalid verification token.')
            return redirect('events:event_list')
