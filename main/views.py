from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import timedelta
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

    # Получаем данные текущего пользователя
    user_profile = request.user.userprofile
    user_sex = user_profile.sex
    user_orientation = user_profile.orientation
    looking_for = user_profile.looking_for
    from_age = user_profile.from_age
    to_age = user_profile.to_age

    # Базовый запрос для пользователей, исключая текущего пользователя и скрытых
    users = User.objects.exclude(id=request.user.id).exclude(id__in=hidden_users).distinct()

    # Фильтрация по looking_for, sex и orientation
    if looking_for == 'relationship':
        if user_orientation == 'not_specified':
            # Без ориентации - ищем противоположный пол
            if user_sex == 'male':
                users = users.filter(userprofile__sex='female', userprofile__orientation='not_specified', userprofile__looking_for='relationship')
            elif user_sex == 'female':
                users = users.filter(userprofile__sex='male', userprofile__orientation='not_specified', userprofile__looking_for='relationship')
        else:
            if user_orientation == 'Homosexuality':
                users = users.filter(userprofile__sex=user_sex, userprofile__orientation='Homosexuality', userprofile__looking_for='relationship')
            elif user_orientation == 'Bisexuality':
                users = users.filter(userprofile__sex__in=['male', 'female'], userprofile__orientation='Bisexuality', userprofile__looking_for='relationship')
            elif user_orientation == 'Asexuality':
                users = users.filter(userprofile__orientation='Asexuality', userprofile__looking_for='relationship')

    elif looking_for == 'friendship':
        # Для дружбы показываем всех, кто ищет дружбу
        users = users.filter(userprofile__looking_for='friendship')

    elif looking_for == 'business_partner':
        # Для бизнес-партнеров показываем всех, кто также ищет бизнес-партнера
        users = users.filter(userprofile__looking_for='business_partner')
    
    # Добавляем фильтрацию по интересам
    user_interests = user_profile.interests.all()
    interest_users = users.filter(userprofile__interests__in=user_interests).distinct()

    # Добавляем фильтрацию по возрасту
    today = date.today()
    current_year = today.year

    # Проверка возрастного диапазона
    if from_age is not None and to_age is not None:
        # Устанавливаем границы для минимального и максимального года рождения
        max_birth_year = current_year - from_age
        min_birth_year = current_year - to_age
        users = users.filter(userprofile__date_of_birth__year__gte=min_birth_year, userprofile__date_of_birth__year__lte=max_birth_year)
        users = users.filter(userprofile__interests__in=user_interests).distinct()
        return render(request, 'main/search_users.html', {'users': users})
    elif from_age is not None:
        max_birth_year = current_year - from_age
        users = users.filter(userprofile__date_of_birth__year__lte=max_birth_year)
        # Добавляем фильтрацию по интересам
        users = users.filter(userprofile__interests__in=user_interests).distinct()
        return render(request, 'main/search_users.html', {'users': users})
    elif to_age is not None:
        print("3")
        min_birth_year = current_year - to_age
        users = users.filter(userprofile__date_of_birth__year__gte=min_birth_year)
        users = users.filter(userprofile__interests__in=user_interests).distinct()
        return render(request, 'main/search_users.html', {'users': users})
   
    else: 
        user_birth_year = user_profile.date_of_birth.year
        final_users = []

        # Ищем ровесников
        same_age_users = users.filter(userprofile__date_of_birth__year=user_birth_year)
        if same_age_users.exists():
            final_users.extend(same_age_users)

        # Переменная для контроля разницы в возрасте
        year_difference = 1
        max_year_difference = 10

        # Ищем пользователей с разницей в возрасте
        while year_difference <= max_year_difference:
            younger_users = users.filter(userprofile__date_of_birth__year=user_birth_year - year_difference)
            older_users = users.filter(userprofile__date_of_birth__year=user_birth_year + year_difference)

            if younger_users.exists():
                final_users.extend(younger_users)
            if older_users.exists():
                final_users.extend(older_users)

            year_difference += 1

            # Удаляем дубликаты, но сохраняем порядок
        final_users = list(dict.fromkeys(final_users))

        # Объединяем результаты по интересам и возрасту, сохраняя порядок
        final_users_set = set(final_users)
        interest_users_set = set(interest_users)

        # Объединяем наборы, сохраняя порядок из final_users
        final_users = [user for user in final_users if user in final_users_set.union(interest_users_set)]

    return render(request, 'main/search_users.html', {'users': final_users})

@login_required
def search_night_partner(request):
    # Проверяем, есть ли у пользователя профиль и интересы
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests:
        return redirect(reverse('main:profile_setup'))

    # Получаем список скрытых пользователей для текущего пользователя
    hidden_users = UserAction.objects.filter(user=request.user, hide=True).values_list('receiver_id', flat=True)

    # Определяем пол для поиска
    user_profile = request.user.userprofile
    search_sex = None

    if user_profile.orientation == 'not_specified':
        # Если ориентация не указана, определяем пол для поиска по полу пользователя
        if user_profile.sex == 'male':
            search_sex = 'female'
        elif user_profile.sex == 'female':
            search_sex = 'male'
    elif user_profile.orientation == 'Homosexuality':
        search_sex = user_profile.sex  # Ищем пользователей того же пола
    elif user_profile.orientation == 'Bisexuality':
        # Ищем пользователей обоих полов
        search_sex = ['male', 'female']
    elif user_profile.orientation == 'Asexuality':
        # Асексуалы ищут только других асексуалов
        search_sex = 'Asexuality'

    # Фильтруем пользователей, исключая скрытых и текущего пользователя
    if search_sex == 'Asexuality':
        users = User.objects.filter(
            userprofile__search_night_partner=True,
            userprofile__sex='Asexuality'
        ).exclude(id=request.user.id).exclude(id__in=hidden_users)
    elif isinstance(search_sex, list):
        users = User.objects.filter(
            userprofile__search_night_partner=True,
            userprofile__sex__in=search_sex
        ).exclude(id=request.user.id).exclude(id__in=hidden_users)
    else:
        users = User.objects.filter(
            userprofile__search_night_partner=True,
            userprofile__sex=search_sex
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
    # Пытаемся получить или создать профиль пользователя
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Обновляем дату рождения
        date_of_birth_str = request.POST.get('date_of_birth')
        if date_of_birth_str:
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                userprofile.date_of_birth = date_of_birth
            except ValueError:
                # Обработка ошибки неверного формата даты
                pass

        # Обновляем пол и ориентацию
        userprofile.sex = request.POST.get('sex')
        userprofile.orientation = request.POST.get('orientation')

        # Обновляем возрастные рамки, обрабатывая пустые строки
        from_age = request.POST.get('from_age', '').strip()
        to_age = request.POST.get('to_age', '').strip()
        
        userprofile.from_age = int(from_age) if from_age.isdigit() else None
        userprofile.to_age = int(to_age) if to_age.isdigit() else None

        # Обновляем поле "looking_for"
        userprofile.looking_for = request.POST.get('looking_for')

        # Обновляем поле "search_night_partner"
        search_night_partner = request.POST.get('search_night_partner')
        userprofile.search_night_partner = bool(search_night_partner)

        # Получаем выбранные интересы и обновляем их
        selected_interests = request.POST.getlist('interests')
        userprofile.interests.clear()
        for interest_name in selected_interests:
            interest, _ = Interest.objects.get_or_create(name=interest_name)
            userprofile.interests.add(interest)

        userprofile.save()
        return redirect('main:search_users')
    return render(request, 'main/profile_setup.html', {
        'userprofile': userprofile,
        'from_age': userprofile.from_age,
        'to_age': userprofile.to_age
    })

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