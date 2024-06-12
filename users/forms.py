from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import User


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'surname', 'nickname', 'profile_icon', 'balance', 'description', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['balance'].widget.attrs['disabled'] = True