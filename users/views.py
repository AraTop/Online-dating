from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView
from friends.models import Friend
from main.models import UserProfile
from users.forms import AlbumForm, PhotoForm, UserForm, UserProfileForm
from users.models import Album, Photo, User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.shortcuts import get_object_or_404

class LoginView(BaseLoginView):
    template_name = 'users/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class LogoutView(BaseLogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            user.is_online = False
            user.last_activity = timezone.now()
            user.save()
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'users/users_register.html'
    success_url = '/users/login/'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Создаем альбом после успешной регистрации пользователя
        Album.objects.create(user=self.object, title="Мой Альбом", is_default=True)
        return response

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

@method_decorator(login_required, name='dispatch')
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
            context['friend_request_received'] = user_detail.pk

        if is_friend == False:
            if not friend_request_sent.exists():
                if not friend_request_received.exists():
                    if user_detail == current_user:
                        pass
                    else:
                        context['no_friend'] = user_detail

        context['user'] = current_user
        user_profile = UserProfile.objects.get(user=user_detail)
        interests = user_profile.interests.all()
        context['interests'] = interests

        albums = Album.objects.filter(user=user_detail)
        context['albums'] = albums

        for album in albums:
            album.cover_photos = album.photos.order_by('-uploaded_at')[:4]

        photos = Photo.objects.filter(album__user=user_detail)
        context['photos'] = photos
        return context

@csrf_exempt
@login_required
def update_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Парсим данные из тела запроса
            is_online = data.get('online')   # Получаем статус online
            if is_online is not None:
                # Обновляем поле is_online непосредственно в модели User
                request.user.is_online = is_online
                request.user.save()

                return JsonResponse({"message": "Status updated", "online": is_online}, status=200)
            else:
                return JsonResponse({"error": "Invalid data"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid method"}, status=405)


@login_required
def add_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.save()
            return redirect('users:user_profile', pk=request.user.pk)
    else:
        form = AlbumForm()
    return render(request, 'users/add_album.html', {'form': form})


@login_required
def add_photo(request):
    if request.method == "POST":
        form = PhotoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            photo = form.save(commit=False)
            # Проверка на пустой альбом
            if not photo.album:
                default_album = Album.objects.filter(user=request.user, is_default=True).first()
                photo.album = default_album
            photo.save()
            return redirect('users:user_profile', pk=request.user.pk)
    else:
        form = PhotoForm(user=request.user)
    
    return render(request, 'users/add_photo.html', {'form': form})


@login_required
def delete_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    # Проверяем, что альбом принадлежит текущему пользователю
    if album.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить чужой альбом.")
    
    if album.is_default:
        return HttpResponseForbidden("Невозможно удалить альбом по умолчанию.")  # Защита альбома по умолчанию
    
    album.delete()
    return redirect('users:user_profile', pk=request.user.pk)


@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Проверяем, что фото принадлежит альбому текущего пользователя
    if photo.album.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить чужую фотографию.")
    
    photo.delete()
    return redirect('users:user_profile', pk=request.user.pk)


@login_required
def edit_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Проверка, что фото принадлежит альбому текущего пользователя
    if photo.album.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать чужую фотографию.")
    
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo, user=request.user)
        if form.is_valid():
            edited_photo = form.save(commit=False)
            if not edited_photo.album:
                default_album = Album.objects.filter(user=request.user, is_default=True).first()
                edited_photo.album = default_album
            edited_photo.save()
            return redirect('users:user_profile', pk=request.user.pk)
    else:
        form = PhotoForm(instance=photo, user=request.user)
    
    return render(request, 'users/edit_photo.html', {'form': form, 'photo': photo})


@login_required
def edit_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    
    # Проверка, что альбом принадлежит текущему пользователю
    if album.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать чужой альбом.")
    
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            return redirect('users:user_profile', pk=request.user.pk)
    else:
        form = AlbumForm(instance=album)
    
    return render(request, 'users/edit_album.html', {'form': form, 'album': album})


@login_required
def album_detail(request, album_id):
    # Получаем альбом по ID
    album = get_object_or_404(Album, id=album_id)
    
    # Получаем все фотографии, связанные с этим альбомом
    photos = Photo.objects.filter(album=album)
    # Передаем в шаблон текущего пользователя и владельца альбома
    return render(request, 'users/album_detail.html', {
        'album': album,
        'photos': photos,
        'current_user': request.user,
        'album_owner': album.user  # Предполагаем, что у Album есть поле `user`
    })

@login_required
def add_photo_in_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)
    
    # Проверка, что альбом принадлежит текущему пользователю
    if album.user != request.user:
        return HttpResponseForbidden("Вы не можете добавлять фотографии в чужой альбом.")
    
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            photo = form.save(commit=False)
            # Привязываем фото к выбранному альбому
            photo.album = album
            photo.save()
            return redirect('users:album_detail', album_id=album.id)
    else:
        form = PhotoForm(user=request.user)
    
    return render(request, 'users/add_photo_in_album.html', {'form': form, 'album': album})