from channels.generic.websocket import AsyncWebsocketConsumer
import json
from users.models import User
from asgiref.sync import sync_to_async
from .models import Message
from datetime import datetime

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
        is_online = receiver.is_online  # Получаем статус пользователя

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
                'is_online': is_online  # Передаем статус онлайн
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
                    'message_id': message_id,
                    'message': new_content,
                }
            )
        except Message.DoesNotExist:
            pass

    async def handle_delete_message(self, data):
        message_id = data['message_id']
        sender_id = self.user.id

        try:
            message = await sync_to_async(Message.objects.get)(id=message_id, sender_id=sender_id)
            await sync_to_async(message.delete)()

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'delete',
                    'message_id': message_id,
                }
            )
        except Message.DoesNotExist:
            pass

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
                'is_online': event['is_online'],  # Получаем статус пользователя
            }))
        
        elif action == 'edit':
            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id'],
                'message': event['message']
            }))
        
        elif action == 'delete':
            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id']
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
            'is_online': event.get('is_online')  # Передаем статус пользователя
        }))