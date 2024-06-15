from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User
from .models import Message
from .forms import MessageForm
from django.db.models import Q

@login_required
def inbox(request):
    # Получаем список всех контактов, с которыми была переписка
    contacts = User.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()

    # Формируем список контактов с пометкой о наличии непрочитанных сообщений
    contacts_with_unread_messages = []
    for contact in contacts:
        if request.user == contact:
            # Пропускаем текущего пользователя
            continue
        
        # Получаем последнее сообщение от контакта
        last_message = Message.objects.filter(
            Q(sender=contact, receiver=request.user) | Q(sender=request.user, receiver=contact)
        ).order_by('-timestamp').first()

        # Проверяем, есть ли непрочитанные сообщения от контакта
        unread_count = Message.objects.filter(sender=contact, receiver=request.user, is_read=False).count()

        # Добавляем контакт в список с пометкой о непрочитанных сообщениях
        contacts_with_unread_messages.append({
            'contact': contact,
            'unread_count': unread_count,
            'last_message': last_message,
        })

    return render(request, 'message/inbox.html', {'contacts_with_unread_messages': contacts_with_unread_messages})


@login_required
def dialog(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.get_dialog(request.user, other_user)

    # Отмечаем сообщения как прочитанные при открытии диалога
    for message in messages.filter(receiver=request.user, is_read=False):
        message.is_read = True
        message.save()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = other_user
            message.save()
            return redirect('dialog', user_id=other_user.id)
    else:
        form = MessageForm()

    return render(request, 'message/dialog.html', {
        'messages': messages,
        'other_user': other_user,
        'form': form
    })
