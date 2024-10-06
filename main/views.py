from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from friends.models import Friend
from .models import Interest, UserAction, UserProfile
from users.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date
from datetime import datetime

@login_required
def search_users(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests.exists():
        return redirect(reverse('main:profile_setup'))

    # Получаем список скрытых пользователей для текущего пользователя
    hidden_users = UserAction.objects.filter(user=request.user, hide=True).values_list('receiver_id', flat=True)

    # Получаем интересы и параметры поиска текущего пользователя
    user_interests = request.user.userprofile.interests.all()
    user_gender = request.user.userprofile.gender
    looking_for = request.user.userprofile.looking_for

    # Инициализируем базовый запрос для пользователей
    users = User.objects.exclude(id=request.user.id).exclude(id__in=hidden_users).distinct()

    # Фильтруем пользователей на основе их пола и поиска
    if looking_for == 'relationship':
        if user_gender == 'male':
            users = users.filter(userprofile__gender='female', userprofile__looking_for='relationship')
        elif user_gender == 'female':
            users = users.filter(userprofile__gender='male', userprofile__looking_for='relationship')
        elif user_gender == 'gay':
            users = users.filter(userprofile__gender='gay', userprofile__looking_for='relationship')
        elif user_gender == 'Lesbian':
            users = users.filter(userprofile__gender='Lesbian', userprofile__looking_for='relationship')
        elif user_gender == 'other':
            users = users.filter(userprofile__gender='other', userprofile__looking_for='relationship')
    elif looking_for == 'friendship':
        # Для дружбы показываем всех, кто ищет дружбу
        users = users.filter(userprofile__looking_for='friendship')
    elif looking_for == 'business_partner':
        # Показываем только тех, кто тоже ищет бизнес-партнеров
        users = users.filter(userprofile__looking_for='business_partner')

    # Добавляем фильтрацию по интересам
    users = users.filter(userprofile__interests__in=user_interests).distinct()

    return render(request, 'main/search_users.html', {'users': users})

@login_required
def search_night_partner(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests:
        return redirect(reverse('main:profile_setup'))

    # Получаем список скрытых пользователей для текущего пользователя
    hidden_users = UserAction.objects.filter(user=request.user, hide=True).values_list('receiver_id', flat=True)

    # Определяем пол, который будем искать в зависимости от пола текущего пользователя
    if request.user.userprofile.gender == 'male':
        search_gender = 'female'
    elif request.user.userprofile.gender == 'female':
        search_gender = 'male'
    elif request.user.userprofile.gender == 'gay':
        search_gender = 'gay'
    elif request.user.userprofile.gender == 'Lesbian':
        search_gender = 'Lesbian'
    elif request.user.userprofile.gender == 'other':
        search_gender = 'other' # или любой другой вариант, если есть

    # Фильтруем пользователей, исключая скрытых и текущего пользователя
    users = User.objects.filter(
        userprofile__search_night_partner=True,
        userprofile__gender=search_gender
    ).exclude(id=request.user.id).exclude(id__in=hidden_users)

    return render(request, 'main/search_night_partner.html', {'users': users})

@login_required
def like_dislike_user(request, user_id, action):
    if request.method == 'POST':
        # Получаем пользователя, который выполняет действие
        current_user = request.user
        
        # Получаем пользователя, к которому применяется действие
        receiver = get_object_or_404(User, id=user_id)
        # Проверяем существование действия между пользователями
        user_action, created = UserAction.objects.get_or_create(
            user=current_user,
            receiver=receiver
        )
        
        if action == 'like':
            # Увеличиваем количество лайков
            user_action.likes += 1
            user_action.hide = False
        elif action == 'dislike':
            # Увеличиваем количество дизлайков
            user_action.dislikes += 1
            user_action.hide = False
        elif action == 'hide':
            # Устанавливаем флаг скрытия
            user_action.hide = True
            user_action.likes = 0
            user_action.dislikes = 0
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
        
        # Сохраняем изменения
        user_action.save()
        
        # Возвращаем успешный ответ
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def profile_setup(request):
    if request.method == 'POST':
        userprofile, created = UserProfile.objects.get_or_create(user=request.user)

        # Обновляем возраст, пол и ищем
        date_of_birth_str = request.POST.get('date_of_birth')
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                userprofile.date_of_birth = date_of_birth
            except ValueError:
                # Обработка ошибки неверного формата даты
                pass

        userprofile.gender = request.POST.get('gender')
        userprofile.looking_for = request.POST.get('looking_for')

        # Получаем выбранные интересы
        selected_interests = request.POST.getlist('interests')
        # Очищаем текущие интересы пользователя
        userprofile.interests.clear()

        # Создаем и добавляем новые интересы
        for interest_name in selected_interests:
            interest, created = Interest.objects.get_or_create(name=interest_name)
            userprofile.interests.add(interest)

        userprofile.save()

        return redirect('main:search_users')
    return render(request, 'main/profile_setup.html')

def home(request):
    user = request.user
    context = {'user': user}
    return render(request, 'main/main_page.html', context)

def hide(request):
    user = request.user
    users = UserAction.objects.filter(user=user, hide=True)
    context = {'users': users}
    return render(request, 'main/hide.html', context)

def remove_hide(request, user_id):
    user = request.user
    user_hide = UserAction.objects.filter(user=user, receiver_id=user_id, hide=True)
    user_hide.update(hide=False)
    return redirect('main:hide')

def search_friends(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests:
        return redirect(reverse('main:profile_setup'))

    query = request.GET.get('q')  # Имя, фамилия или отчество
    gender = request.GET.get('gender')  # Пол
    is_online = request.GET.get('is_online')  # Статус пользователя (онлайн/оффлайн)
    interests_query = request.GET.get('interests')  # Интересы
    age_from = request.GET.get('age_from')  # Возраст от
    age_to = request.GET.get('age_to')  # Возраст до

    # Изначально фильтруем всех пользователей, кроме текущего
    results = User.objects.filter(userprofile__isnull=False).exclude(id=request.user.id)

    # Фильтр по имени, фамилии или отчеству
    if query:
        results = results.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(surname__icontains=query)
        )

    # Фильтр по полу
    if gender:
        results = results.filter(userprofile__gender=gender)

    # Фильтр по интересам
    if interests_query:
        results = results.filter(userprofile__interests__name__icontains=interests_query)

    # Фильтр по возрасту
    today = date.today()
    if age_from:
        min_birthdate = today.replace(year=today.year - int(age_from))
        results = results.filter(userprofile__date_of_birth__lte=min_birthdate)
    
    if age_to:
        max_birthdate = today.replace(year=today.year - int(age_to))
        results = results.filter(userprofile__date_of_birth__gte=max_birthdate)

    # Фильтр по статусу (онлайн/оффлайн)
    if is_online:
        if is_online == 'true':  # Если выбран статус онлайн
            results = results.filter(is_online=True)
        elif is_online == 'false':  # Если выбран статус оффлайн
            results = results.filter(is_online=False)

    # Фильтрация друзей с подтвержденным статусом дружбы
    confirmed_friends = results.filter(
        Q(friend_list__status='accepted', friend_list__friend=request.user) |  # у кого я в друзьях подтвержденных
        Q(friend_of_list__status='accepted', friend_of_list__user=request.user)  # кого я пригласил в друзьях подтвержденных
    ).distinct()

    # Фильтрация друзей, которые мне кинули запрос в дружбу
    pending_requests = results.filter(
        Q(friend_list__status='pending', friend_list__friend=request.user)
    ).distinct()
    
    # Фильтрация друзей, которым я кинул запрос в дружбу
    pending_requests_reverse = Friend.objects.filter(
        user=request.user,  # Текущий пользователь отправил запрос
        status='pending'     # Статус "ожидание"
    ).values('friend')  # Получаем только друзей, которым был отправлен запрос

    # Фильтрация пользователей, которые не являются друзьями с подтвержденным статусом
    non_friends = results.exclude(id__in=confirmed_friends).exclude(id__in=pending_requests).exclude(id__in=pending_requests_reverse)

    # Словарь для хранения количества общих друзей
    common_friends_count = {}

    # Получаем список всех друзей текущего пользователя
    my_friends = Friend.objects.filter(
        Q(user=request.user) | Q(friend=request.user),
        status='accepted'
    ).values_list('user', 'friend')

    # Преобразуем список друзей текущего пользователя в множество и исключаем самого пользователя
    my_friends_ids = set()
    for pair in my_friends:
        my_friends_ids.update(pair)
    my_friends_ids.discard(request.user.id)  # Убираем ID текущего пользователя

    # Найдем пользователей с общими друзьями и посчитаем их количество
    for user in results:  # Считаем общих друзей для всех пользователей, а не только для non_friends
        # Получаем всех друзей пользователя
        user_friends = Friend.objects.filter(
            Q(user=user) | Q(friend=user),
            status='accepted'
        ).values_list('user', 'friend')

        # Преобразуем список друзей пользователя в множество и исключаем его самого
        user_friends_ids = set()
        for pair in user_friends:
            user_friends_ids.update(pair)
        user_friends_ids.discard(user.id)  # Убираем ID самого пользователя

        # Считаем общих друзей между текущим пользователем и найденными пользователями
        common_friends = my_friends_ids.intersection(user_friends_ids)
        common_friends_count[user.id] = len(common_friends)

    # Сначала друзья, потом те, которые вам отправили запрос, потом которым вы отправили запрос, и другие пользователи
    results = list(confirmed_friends) + list(pending_requests) + list(User.objects.filter(id__in=pending_requests_reverse)) + list(non_friends)

    # Добавляем количество общих друзей к каждому пользователю
    for user in results:
        user.common_friends_count = common_friends_count.get(user.id, 0)  # Добавляем поле с количеством общих друзей

    context = {
        'query': query,
        'results': results,
        'friends': confirmed_friends,
        'pending_requests': pending_requests,
        'pending_requests_reverse': User.objects.filter(id__in=pending_requests_reverse),  # Для отображения в шаблоне
        'common_friends_count': common_friends_count  # Для отображения общего количества друзей
    }
    
    return render(request, 'main/search_friends.html', context)