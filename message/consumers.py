from channels.generic.websocket import AsyncWebsocketConsumer
import json
from users.models import User
from asgiref.sync import sync_to_async
from .models import Message
from datetime import datetime
from django.db.models import Q

# Хранилище для подключенных пользователей
connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_user_id = int(self.scope['url_route']['kwargs']['user_id'])
        self.room_group_name = f'chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}'
        
        # Подключение к группе чата
        connected_users[self.user.id] = {
            'channel_name': self.channel_name,
            'room_group_name': self.room_group_name
        }

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Подключение к группе уведомлений
        self.notification_group_name = f'notifications_{self.user.id}'
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        if self.user.id in connected_users:
            del connected_users[self.user.id] 

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Отключение от группы уведомлений
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'new':
            await self.handle_new_message(data)
        elif action == 'edit':
            await self.handle_edit_message(data)
        elif action == 'delete':
            await self.handle_delete_message(data)
        elif action == 'delete_chat':
            await self.handle_delete_chat(data)
        elif action == 'request_status':
            await self.handle_request_status(data)

    async def handle_new_message(self, data):
        message_content = data['message']
        sender_id = self.user.id

        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=self.other_user_id)
        
        is_read = (
            sender_id in connected_users and 
            self.other_user_id in connected_users and 
            connected_users[sender_id]['room_group_name'] == self.room_group_name and 
            connected_users[self.other_user_id]['room_group_name'] == self.room_group_name
        )

        message = await sync_to_async(Message.objects.create)( 
            sender=sender,
            receiver=receiver,
            content=message_content,
            is_read=is_read
        )

        timestamp = datetime.now().isoformat()

        # Передача статуса онлайн
        is_online = receiver.is_online

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'new',
                'message_id': message.id,
                'message': message.content,
                'sender': sender.first_name,
                'sender_id': sender.id,
                'timestamp': timestamp,
                'profile_icon': sender.profile_icon.url if sender.profile_icon else '/static/images/default-profile.png',
                'is_read': is_read,
                'is_online': is_online
            }
        )
        
        # Отправка уведомления о новом сообщении
        await self.channel_layer.group_send(
            f'notifications_{receiver.id}',
            {
                'type': 'notify_new_message',
                'contact_id': sender.id,
                'message': message.content,
                'sender_profile_icon_url': sender.profile_icon.url if sender.profile_icon else '/static/images/default-profile.png',
                'sender_first_name': sender.first_name,
                'sender_last_name': sender.last_name,
                'unread_count': await sync_to_async(Message.objects.filter(receiver=receiver, is_read=False).count)()
            }
        )

    async def handle_edit_message(self, data):
        message_id = data['message_id']
        new_content = data['message']
        sender_id = self.user.id

        try:
            message = await sync_to_async(Message.objects.get)(id=message_id, sender_id=sender_id)
            message.content = new_content
            message.timestamp = datetime.now()
            await sync_to_async(message.save)()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'edit',
                    'contact_id': sender_id,
                    'message_id': message_id,
                    'message': new_content,
                }
            )
            receiver_id = await sync_to_async(lambda: message.receiver.id)()
            await self.channel_layer.group_send(
                f'notifications_{receiver_id}',
                {
                    'type': 'chat_message',
                    'action': 'edit',
                    'contact_id': sender_id,
                    'message_id': message_id,
                    'message': new_content,
                    'sender_profile_icon_url': data.get('sender_profile_icon_url'),
                    'sender_first_name': data.get('sender_first_name'),
                }
            )
        except Message.DoesNotExist:
            pass

    async def handle_delete_message(self, data):
        message_id = data['message_id']
        sender_id = self.user.id

        try:
            message = await sync_to_async(Message.objects.get)(id=message_id, sender_id=sender_id)
            receiver_id = await sync_to_async(lambda: message.receiver.id)()
            await sync_to_async(message.delete)()
                
            # Получаем последнее сообщение и извлекаем его данные
            last_message = await sync_to_async(
                lambda: Message.objects.filter(
                    (Q(sender_id=sender_id, receiver_id=receiver_id) | Q(sender_id=receiver_id, receiver_id=sender_id))
                ).order_by('-timestamp').first()
            )()

            # Получаем фото отправителя и получателя по их ID
            sender_user = await sync_to_async(lambda: User.objects.get(id=sender_id))()
            receiver_user = await sync_to_async(lambda: User.objects.get(id=receiver_id))()

            sender_photo_url = sender_user.profile_icon.url if sender_user.profile_icon else '/static/images/default-profile.png'
            receiver_photo_url = receiver_user.profile_icon.url if receiver_user.profile_icon else '/static/images/default-profile.png'

            # Преобразуем последнее сообщение в словарь
            last_message_data = {
                'id': last_message.pk,
                'sender_id': last_message.sender_id,
                'receiver_id': last_message.receiver_id,
                'content': last_message.content,
                'timestamp': last_message.timestamp.isoformat() if last_message else None
            } if last_message else None
            
            # Проверяем, есть ли последнее сообщение
            if last_message is None:
                # Уведомляем об удалении чата
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'action': 'delete_chat',
                        'contact_id': receiver_id,
                        'sender_id': sender_id
                    }
                )
                
                # Уведомляем вторую сторону об удалении чата
                await self.channel_layer.group_send(
                    f'notifications_{receiver_id}',  # Или другой идентификатор, чтобы гарантировать уведомление второй стороне
                    {
                        'type': 'chat_message',
                        'action': 'delete_chat',
                        'contact_id': sender_id,
                        'sender_id': receiver_id
                    }
                )

            # Уведомляем получателя и передаем last_message в виде словаря
            await self.channel_layer.group_send(
                f'notifications_{receiver_id}',
                {
                    'type': 'notify_deleted_message',
                    'message_id': message_id,
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'last_message': last_message_data,
                    'sender_photo_url': sender_photo_url,
                    'receiver_photo_url': receiver_photo_url,
                }
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete',
                    'message_id': message_id,
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'last_message': last_message_data,
                    'sender_photo_url': sender_photo_url,
                    'receiver_photo_url': receiver_photo_url,
                }
            )
        except Message.DoesNotExist:
            pass

    async def handle_delete_chat(self, data):
        sender_id = self.user.id
        receiver_id = data['contact_id']

        #print(f"Sender ID: {sender_id}, Receiver ID: {receiver_id}")

        # Удаление всех сообщений между пользователями
        deleted_count, _ = await sync_to_async(Message.objects.filter(
            Q(sender_id=sender_id, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver_id=sender_id)
        ).delete)()
        
        #print(f"Messages deleted: {deleted_count}")

        # Если удаление прошло успешно, уведомляем обе стороны
        if deleted_count > 0:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete_chat',
                    'contact_id': receiver_id,
                    'sender_id': sender_id
                }
            )
            
            # Уведомляем вторую сторону об удалении чата
            await self.channel_layer.group_send(
                f'notifications_{receiver_id}',  # Или другой идентификатор, чтобы гарантировать уведомление второй стороне
                {
                    'type': 'chat_message',
                    'action': 'delete_chat',
                    'contact_id': sender_id,
                    'sender_id': receiver_id
                }
            )
        else:
            print("No messages were deleted.")
            
    async def handle_request_status(self, data):
        user_id = data['user_id']
        other_user = await sync_to_async(User.objects.get)(id=user_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'action': 'status_update',
                'is_online': other_user.is_online,
                'last_activity': other_user.last_activity.isoformat() if other_user.last_activity else None
            }
        )

    async def chat_message(self, event):
        action = event['action']
        
        if action == 'new':
            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id'],
                'message': event['message'],
                'sender': event['sender'],
                'sender_id': event['sender_id'],
                'timestamp': event['timestamp'],
                'profile_icon': event['profile_icon'],
                'is_read': event['is_read'],
                'is_online': event['is_online'],
            }))
        
        elif action == 'edit':
            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id'],
                'message': event['message'],
                'contact_id': event['contact_id']
            }))
        
        elif action == 'delete':
            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id'],
                'sender_id': event['sender_id'],
                'receiver_id': ['receiver_id'],
                'last_message': event['last_message'],
                'sender_photo_url': event['sender_photo_url'],
                'receiver_photo_url': event['receiver_photo_url'],
            }))
        
        elif action == 'delete_chat':
            await self.send(text_data=json.dumps({
                'action': action,
                'contact_id': event['contact_id'],
                'message': 'Chat has been deleted'  # Можно передать сообщение, если нужно
            }))
        
        elif action == 'status_update':
            await self.send(text_data=json.dumps({
                'action': 'status_update',
                'is_online': event['is_online'],
                'last_activity': event['last_activity']
            }))

    async def notify_new_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'contact_id': event['contact_id'],
            'message': event['message'],
            'unread_count': event['unread_count'],
            'sender_profile_icon_url': event.get('sender_profile_icon_url'),
            'sender_first_name': event.get('sender_first_name'),
            'sender_last_name': event.get('sender_last_name'),
            'is_online': event.get('is_online')
        }))

    async def notify_deleted_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'receiver_id': ['receiver_id'],
            'last_message': event['last_message'],
            'sender_photo_url': event['sender_photo_url'],
            'receiver_photo_url': event['receiver_photo_url'],
        }))