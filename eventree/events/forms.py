from django import forms
from .models import Event
from .registrations.models import Registration

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = []  # No fields needed as we'll set event and user in the view
        
    def clean(self):
        cleaned_data = super().clean()
        if hasattr(self, 'instance') and hasattr(self.instance, 'event') and self.instance.event:
            if not self.instance.event.is_available:
                raise forms.ValidationError("This event is already full.")
        return cleaned_data
