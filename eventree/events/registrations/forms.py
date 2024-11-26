from django import forms
from .models import Registration, Invitation

class InviteGuestForm(forms.ModelForm):
    email = forms.EmailField(
        label="Guest's Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Invitation
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.registration = kwargs.pop('registration', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        # Check if this email is already registered for this event
        if self.registration:
            if self.registration.event.registrations.filter(user__email=email).exists():
                raise forms.ValidationError(
                    "This email is already registered for this event."
                )
        return email
