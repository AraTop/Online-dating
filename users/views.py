from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView
from friends.models import Friend
from users.forms import UserForm, UserProfileForm
from users.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

class LoginView(BaseLoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class LogoutView(BaseLogoutView):
    pass


class RegisterView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/users_register.html'
    success_url = '/users/login/'


@method_decorator(login_required, name='dispatch')
class UserDeleteView(DeleteView):
    model = User

    def get_object(self, queryset=None):
        user = super().get_object(queryset)
        user.delete()


@method_decorator(login_required, name='dispatch')
class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class UserDetailView(DetailView):
    model = User
    template_name = 'users/users_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем пользователя, чей профиль просматривается
        user_detail = self.get_object()
        
        # Текущий пользователь, просматривающий профиль
        current_user = self.request.user
        
        # Проверяем, является ли текущий пользователь другом пользователя user_detail
        is_friend = Friend.objects.filter(
            Q(user=user_detail, friend=current_user, status='accepted') |
            Q(user=current_user, friend=user_detail, status='accepted')
        ).exists()
        
        # Проверяем, есть ли заявка в друзья от текущего пользователя к пользователю user_detail
        friend_request_sent = Friend.objects.filter(
            user=current_user, friend=user_detail, status='pending'
        )
        
        # Проверяем, есть ли заявка в друзья от пользователя user_detail к текущему пользователю
        friend_request_received = Friend.objects.filter(
            user=user_detail, friend=current_user, status='pending'
        )
        
        # Добавляем полученные данные в контекст
        context['is_friend'] = is_friend
        if friend_request_sent:
            context['friend_request_sent'] = user_detail.pk
        
        if friend_request_received:
            context['friend_request_received'] = current_user.pk

        if is_friend == False:
            if not friend_request_sent.exists():
                if not friend_request_received.exists():
                    context['no_friend'] = user_detail

        context['user'] = current_user
        return context
