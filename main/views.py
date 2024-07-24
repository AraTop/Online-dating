from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import UserProfile
from users.models import User

@login_required
def search_users(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.interests:
        return redirect(reverse('main:profile_setup'))

    users = User.objects.filter(
        userprofile__interests__icontains=request.user.userprofile.interests,
        userprofile__gender='female' if request.user.userprofile.gender == 'male' else 'male'
    ).exclude(id=request.user.id)

    return render(request, 'main/search_users.html', {'users': users})

@login_required
def search_night_partner(request):
    # Проверяем, что у пользователя есть профиль
    if not hasattr(request.user, 'userprofile'):
        return redirect(reverse('main:profile_setup'))

    users = User.objects.filter(
        userprofile__search_night_partner=True,
        userprofile__gender='female' if request.user.userprofile.gender == 'male' else 'male'
    ).exclude(id=request.user.id)

    return render(request, 'main/search_night_partner.html', {'users': users})

@login_required
def like_dislike_user(request, user_id, action):
    # This view handles liking or disliking a user
    # Add your own logic to handle the like/dislike action
    return redirect('main:search_users')

@login_required
def profile_setup(request):
    if request.method == 'POST':
        userprofile, created = UserProfile.objects.get_or_create(user=request.user)
        userprofile.interests = request.POST.get('interests')
        userprofile.age = request.POST.get('age')
        userprofile.gender = request.POST.get('gender')
        userprofile.looking_for = request.POST.get('looking_for')
        userprofile.search_night_partner = 'search_night_partner' in request.POST
        userprofile.save()
        return redirect('main:search_users')
    return render(request, 'main/profile_setup.html')

def home(request):
    user = request.user
    context = {'user': user}
    return render(request, 'main/main_page.html', context)
