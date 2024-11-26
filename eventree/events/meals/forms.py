from django import forms
from .models import MealSelection, Meal

class MealSelectionForm(forms.ModelForm):
    class Meta:
        model = MealSelection
        fields = ['meal', 'quantity']
        widgets = {
            'meal': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            })
        }

    def __init__(self, *args, **kwargs):
        registration = kwargs.pop('registration', None)
        super().__init__(*args, **kwargs)
        if registration:
            # Only show meals from the event this registration is for
            self.fields['meal'].queryset = Meal.objects.filter(
                event=registration.event,
                is_active=True
            )

    def clean(self):
        cleaned_data = super().clean()
        meal = cleaned_data.get('meal')
        quantity = cleaned_data.get('quantity')

        if meal and quantity:
            if not meal.is_available():
                raise forms.ValidationError("This meal is no longer available.")
            
            if quantity > meal.remaining_quantity():
                raise forms.ValidationError(
                    f"Only {meal.remaining_quantity()} servings of this meal are available."
                )
        
        return cleaned_data
