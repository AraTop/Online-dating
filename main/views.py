from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Interest, UserAction, UserProfile
from users.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q

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
        userprofile.age = request.POST.get('age')
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
    interests_query = request.GET.get('interests')  # Интересы

    results = User.objects.none()  # Начнем с пустого QuerySet, чтобы результат был пустым, если запрос не заполнен

    if query or gender or interests_query:
        # Поиск всех пользователей, у которых есть профиль, и исключаем самого себя
        results = User.objects.filter(userprofile__isnull=False).exclude(id=request.user.id)

        # Фильтр по имени, фамилии или отчеству
        if query:
            results = results.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(surname__icontains=query)  # Добавляем фильтрацию по отчеству
            )

        # Фильтр по полу
        if gender:
            results = results.filter(userprofile__gender=gender)

        # Фильтр по интересам
        if interests_query:
            results = results.filter(userprofile__interests__name__icontains=interests_query)

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'main/search_friends.html', context)