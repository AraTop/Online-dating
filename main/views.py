from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Interest, UserAction, UserProfile
from users.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required
def search_users(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests.exists():
        return redirect(reverse('main:profile_setup'))

    # Получаем список скрытых пользователей для текущего пользователя
    hidden_users = UserAction.objects.filter(user=request.user, hide=True).values_list('receiver_id', flat=True)

    # Получаем интересы текущего пользователя
    user_interests = request.user.userprofile.interests.all()

    # Фильтруем пользователей, исключая скрытых и текущего пользователя
    users = User.objects.filter(
        userprofile__interests__in=user_interests,
        userprofile__gender='female' if request.user.userprofile.gender == 'male' else 'male'
    ).exclude(id=request.user.id).exclude(id__in=hidden_users).distinct()

    return render(request, 'main/search_users.html', {'users': users})

@login_required
def search_night_partner(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests:
        return redirect(reverse('main:profile_setup'))

    # Получаем список скрытых пользователей для текущего пользователя
    hidden_users = UserAction.objects.filter(user=request.user, hide=True).values_list('receiver_id', flat=True)

    # Фильтруем пользователей, исключая скрытых и текущего пользователя
    users = User.objects.filter(
        userprofile__search_night_partner=True,
        userprofile__gender='female' if request.user.userprofile.gender == 'male' else 'male'
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
        print(selected_interests)
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
