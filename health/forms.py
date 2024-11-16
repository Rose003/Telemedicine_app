from django import forms
from .models import Patients
from django.contrib.auth.hashers import make_password

class PatientRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    password_hash = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Patients
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 
                 'gender', 'address', 'password_hash']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[
                ('male', 'Male'),
                ('female', 'Female'),
                ('other', 'Other')
            ])
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password_hash') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        patient = super().save(commit=False)
        patient.password_hash = make_password(self.cleaned_data['password_hash'])
        if commit:
            patient.save()
        return patient
