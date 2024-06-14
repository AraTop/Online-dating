from django.http import HttpResponseForbidden
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from users.models import User
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Friend
from django.db.models import Q
from django.contrib.auth.decorators import login_required

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
        
        # Пытаемся найти запись дружбы с текущим пользователем
        try:
            return Friend.objects.get(user=current_user, friend=friend)
        except Friend.DoesNotExist:
            # Если такой записи нет, проверяем обратную связь
            return get_object_or_404(Friend, user=friend, friend=current_user)

    def delete(self, request, *args, **kwargs):
        # Получаем объект дружбы
        friend_obj = self.get_object()
        
        # Удаляем объект дружбы
        friend_obj.delete()
        
        # Возвращаемся на страницу списка друзей
        return super().delete(request, *args, **kwargs)


class FriendListView(LoginRequiredMixin, ListView):
    template_name = 'friends/friend_list.html'
    context_object_name = 'friends'

    def get_queryset(self):
        current_user = self.request.user
        
        friends = Friend.objects.filter(
            Q(user=current_user) | Q(friend=current_user),
            status='accepted'
        )

        friends_list = []
        for friend in friends:
            if friend.user != current_user:
                friends_list.append(friend.user)
            if friend.friend != current_user:
                friends_list.append(friend.friend)

        unique_friends = list(set(friends_list))
        return unique_friends
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_user = self.request.user
        friends_outgoing = Friend.objects.filter(user=current_user, status='pending')
        friend_requests_count = Friend.objects.filter(friend=current_user, status='pending').count()
        friends_count = Friend.objects.filter(
            Q(user=current_user) | Q(friend=current_user),
            status='accepted'
        ).count()
        context['user_request'] = current_user
        context['friends_outgoing_count'] = friends_outgoing.count()
        context['friend_requests_count'] = friend_requests_count
        context['friends_count'] = friends_count

        return context


def friend_requests(request):
    user = request.user
    friends_outgoing = Friend.objects.filter(user=user, status='pending')
    friend_requests = Friend.objects.filter(friend=user, status='pending')
    friends_count = Friend.objects.filter(
            Q(user=user) | Q(friend=user),
            Q(status='accepted')
        ).count()
    context = {
        'user_request': user,
        'friends_outgoing_count': friends_outgoing.count(),
        'friends_request_count': friend_requests.count(),
        'friends_count': friends_count,
        'user': user,
        'friend_requests': friend_requests,
    }
    return render(request, 'friends/friend_request.html', context)


def friend_outgoing(request):
    user = request.user
    friends_outgoing = Friend.objects.filter(user=user, status='pending')
    friend_requests = Friend.objects.filter(friend=user, status='pending')
    friends_count = Friend.objects.filter(
            Q(user=user) | Q(friend=user),
            Q(status='accepted')
        ).count()
    context = {
        'user_request': user,
        'friends_outgoing': friends_outgoing,
        'friends_outgoing_count': friends_outgoing.count(),
        'friends_request_count': friend_requests.count(),
        'friends_count': friends_count,
        'user': user,
        'friend_requests': friend_requests,
    }
    return render(request, 'friends/friend_outgoing.html', context)


@login_required
def friend_add(request, pk):
    friend = get_object_or_404(User, id=pk)
    Friends = Friend.objects.filter(friend=friend).first()
    # Получаем запрос в друзья по идентификатору pk
    friend_request = get_object_or_404(Friend, id=Friends.pk)

    # Изменяем статус на 'accepted'
    if friend_request.status == 'pending':
        friend_request.status = 'accepted'
        friend_request.save()

    return redirect('friends:friend_list')

@login_required
def friend_reject(request, pk):
    friend = get_object_or_404(User, id=pk)
    Friend.objects.filter(user=request.user, friend=friend).delete()
    
    return redirect('friends:friend_list')
