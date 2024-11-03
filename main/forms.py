from django import forms
from .models import Interest, UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['list_interests', 'age', 'sex', 'orientation', 'from_age', 'to_age', 'search_night_partner', 'looking_for', 'date_of_birth']
