from django.views.generic import CreateView, DeleteView, ListView, DetailView
from users.models import User
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Friend
from django.db.models import Q


class AddFriendView(LoginRequiredMixin, CreateView):
    model = Friend
    fields = ['__all__']  # Здесь можно добавить нужные поля, если они есть
    success_url = reverse_lazy('friends:friend_list')

    def form_valid(self, form):
        friend_username = self.kwargs['username']
        friend = get_object_or_404(User, username=friend_username)
        form.instance.user = self.request.user
        form.instance.friend = friend
        # Проверка на существование дружбы с обеих сторон
        if Friend.objects.filter(user=self.request.user, friend=friend).exists():
            return redirect(self.success_url)
        # Создание обратного отношения дружбы
        Friend.objects.create(user=friend, friend=self.request.user)
        return super().form_valid(form)


class RemoveFriendView(LoginRequiredMixin, DeleteView):
    model = Friend
    success_url = reverse_lazy('friends:friend_list')

    def get_object(self, queryset=None):
        friend_username = self.kwargs['username']
        friend = get_object_or_404(User, username=friend_username)
        # Найдите дружбу и обратную дружбу
        return Friend.objects.filter(user=self.request.user, friend=friend).first()

    def delete(self, request, *args, **kwargs):
        # Удаление дружбы с обеих сторон
        friend_username = self.kwargs['username']
        friend = get_object_or_404(User, username=friend_username)
        Friend.objects.filter(user=self.request.user, friend=friend).delete()
        Friend.objects.filter(user=friend, friend=self.request.user).delete()
        return redirect(self.success_url)


class FriendListView(LoginRequiredMixin, ListView):
    template_name = 'friends/friend_list.html'
    model = Friend
    context_object_name = 'friends'

    def get_queryset(self):
        # Получаем текущего пользователя из сессии
        current_user = self.request.user

        # Получаем всех друзей текущего пользователя
        friends = Friend.objects.filter(Q(user=current_user) | Q(friend=current_user))

        # Исключаем текущего пользователя из списка друзей
        friends = friends.exclude(user=current_user)

        # Меняем роли друзей, чтобы они были представлены как друзья текущего пользователя
        for friend in friends:
            friend_user = friend.user
            friend.user = friend.friend
            friend.friend = friend_user

        return friends


class FriendDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'friends/friend_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавьте сюда любую дополнительную информацию, которую нужно передать в шаблон
        return context
