from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from users.models import Album, Photo, User


class UserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'surname', 'profile_icon', 'balance', 'description')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['balance'].widget.attrs['disabled'] = True


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description']


class PhotoForm(forms.ModelForm):
    album = forms.ModelChoiceField(
        queryset=Album.objects.none(), 
        required=False, 
        label="Выберите альбом (необязательно)"
    )

    class Meta:
        model = Photo
        fields = ['image', 'description', 'album']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PhotoForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['album'].queryset = Album.objects.filter(user=user)