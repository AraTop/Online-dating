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
        Friend.objects.create(user=self.request.user, friend=friend)
        return super().form_valid(form)


class RemoveFriendView(LoginRequiredMixin, DeleteView):
    model = Friend
    success_url = reverse_lazy('friends:friend_list')

    def get_object(self, queryset=None):
        # Получаем текущего пользователя
        current_user = self.request.user

        # Получаем ID друга из URL
        friend_id = self.kwargs['friend_id']
        # Находим объект User для друга
        friend = get_object_or_404(User, id=friend_id)
        # Ищем запись дружбы между текущим пользователем и другом
        return Friend.objects.filter(user=current_user, friend=friend).all()

    def delete(self, request, *args, **kwargs):
        # Получаем ID друга из URL
        friend_id = self.kwargs['friend_id']
        
        # Находим объект User для друга
        friend = get_object_or_404(User, id=friend_id)

        # Удаление дружбы с обеих сторон
        Friend.objects.filter(user=self.request.user, friend=friend).delete()
        Friend.objects.filter(user=friend, friend=self.request.user).delete()

        # Возвращаем результат
        return super().delete(request, *args, **kwargs)


class FriendListView(LoginRequiredMixin, ListView):
    template_name = 'friends/friend_list.html'
    model = Friend
    context_object_name = 'friends'

    def get_queryset(self):
        # Получаем текущего пользователя из сессии
        current_user = self.request.user
        
        # Получаем всех друзей текущего пользователя, включая принятые и отклоненные заявки на дружбу
        friends = Friend.objects.filter(
            Q(user=current_user) | Q(friend=current_user),
            Q(status='accepted') | Q(status='Rejected')  # Включаем принятые и отклоненные заявки
        ).exclude(
            Q(user=current_user) & Q(friend=current_user)
        )
        
        return friends

