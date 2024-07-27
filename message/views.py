from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User
from .models import Message
from .forms import MessageForm
from django.db.models import Q
from django.http import JsonResponse

@login_required
def inbox(request):
    contacts_with_unread_messages = []
    contacts = User.objects.filter(
        Q(sent_messages__receiver=request.user) |
        Q(received_messages__sender=request.user)
    ).distinct()

    contacts_with_unread_messages = []

    for contact in contacts:
        # Получение последнего сообщения
        last_message = Message.objects.filter(
            Q(sender=contact, receiver=request.user) |
            Q(sender=request.user, receiver=contact)
        ).order_by('-timestamp').first()

        unread_count = Message.objects.filter(
            sender=contact,
            receiver=request.user,
            is_read=False
        ).count()

        room_name = f'{min(request.user.id, contact.id)}_{max(request.user.id, contact.id)}'
        print(room_name)
        contacts_with_unread_messages.append({
            'contact': contact,
            'last_message': last_message,
            'unread_count': unread_count,
            'last_message_sender': last_message.sender if last_message else None,  # Отправитель последнего сообщения
            'room_name': room_name
            
        })

    # Сортировка контактов по времени последнего сообщения, чтобы новые были сверху
    contacts_with_unread_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else None,
        reverse=True
    )

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
        'form': form,
        'other_user': other_user
    })

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    message.delete()
    return redirect('dialog', user_id=message.receiver.id if message.sender == request.user else message.sender.id)

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    if request.method == 'POST':
        new_content = request.POST.get('content', '')
        message.content = new_content
        message.save()
    
    # Получаем ID пользователя, с которым ведется диалог
    dialog_user_id = message.receiver_id
    
    # После редактирования возвращаем пользователя на страницу диалога
    return redirect('dialog', user_id=dialog_user_id)
