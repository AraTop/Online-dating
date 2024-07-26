from django import forms
from .models import Interest, UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['list_interests', 'age', 'gender']
