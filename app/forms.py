from django.core.exceptions import ValidationError

from django import forms
from .  models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["full_name", "phone", "email" ,"message"]

        # Move the widgets dictionary inside the Meta class
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Enter your name', 
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter phone number', 
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address', 
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Your message', 
                'class': 'form-control',
                'rows': 4
            }),
        }

        def clean_full_name(self):
            data = self.cleaned_data["full_name"]

            if data or len(data.strip()) < 3:
                raise ValidationError("Name should be more than 3 letters")
            
            return data
