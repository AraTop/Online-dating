from django.http import HttpResponseForbidden
from django.views.generic import CreateView, DeleteView, ListView, DetailView, View
from users.models import User
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Friend
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.decorators import method_decorator

@login_required
def AddFriendView(request, pk):
    friend_pk = pk
    friend = get_object_or_404(User, pk=friend_pk)
    
    # Проверяем, существует ли уже запрос или отношение дружбы
    if Friend.objects.filter(user=request.user, friend=friend).exists():
        messages.info(request, 'Запрос на добавление в друзья уже отправлен или пользователи уже друзья.')
        return JsonResponse({'status': 'exists', 'message': 'Запрос на добавление в друзья уже отправлен или пользователи уже друзья.'})

    # Создаем новый запрос на добавление в друзья
    friend_request, created = Friend.objects.get_or_create(
        user=request.user,
        friend=friend,
        status='pending'
    )

    if created:
        messages.success(request, 'Запрос на добавление в друзья отправлен.')
        return JsonResponse({'status': 'created', 'message': 'Запрос на добавление в друзья отправлен.'})
    else:
        messages.info(request, 'Запрос на добавление в друзья уже отправлен.')
        return JsonResponse({'status': 'exists', 'message': 'Запрос на добавление в друзья уже отправлен.'})

@method_decorator(login_required, name='dispatch')
class RemoveFriendView(LoginRequiredMixin, View):
    success_url = reverse_lazy('friends:friend_list')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Получаем текущего пользователя
        current_user = self.request.user
        friend_id = self.kwargs['friend_id']
        
        # Получаем друга, которого нужно удалить
        friend = get_object_or_404(User, id=friend_id)

        # Находим запись дружбы
        friend_obj = None
        try:
            friend_obj = Friend.objects.get(user=current_user, friend=friend)
        except Friend.DoesNotExist:
            friend_obj = get_object_or_404(Friend, user=friend, friend=current_user)

        # Изменяем статус на 'pending'
        friend_obj.status = 'pending'
        friend_obj.save()
        
        # Добавляем сообщение об успехе
        messages.success(request, 'Дружба удалена. Заявка на добавление в друзья отправлена.')

        # Проверка на AJAX-запрос
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'pending', 'message': 'Дружба удалена. Заявка на добавление в друзья отправлена.'})
        else:
            # Перенаправляем на предыдущую страницу или на список друзей
            return redirect(request.META.get('HTTP_REFERER', self.success_url))

@method_decorator(login_required, name='dispatch')
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


@login_required
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


@login_required
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
    
    # Находим первый запрос на добавление в друзья
    friend_request = get_object_or_404(Friend, id=Friends.pk)
    
    if friend_request.status == 'pending':
        friend_request.status = 'accepted'
        friend_request.save()
        messages.success(request, f'Теперь вы друзья с {friend.username}.')

    else:
        messages.error(request, 'Запрос на добавление в друзья не найден.')
    
    # Перенаправляем на предыдущую страницу или на список друзей
    return redirect(request.META.get('HTTP_REFERER', 'friends:friend_list'))

@login_required
def friend_reject(request, pk):
    friend = get_object_or_404(User, id=pk)
    Friend.objects.filter(user=request.user, friend=friend).delete()
    
    return redirect(request.META.get('HTTP_REFERER', 'friends:friend_list'))
