from channels.generic.websocket import AsyncWebsocketConsumer
import json
from users.models import User
from asgiref.sync import sync_to_async
from .models import Message
from datetime import datetime
connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_user_id = int(self.scope['url_route']['kwargs']['user_id'])
        self.room_group_name = f'chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}'

        # Сохраняем room_group_name вместе с channel_name
        connected_users[self.user.id] = {
            'channel_name': self.channel_name,
            'room_group_name': self.room_group_name
        }
        
        await self.channel_layer.group_add(
            self.room_group_name,
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

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'new':
            await self.handle_new_message(data)
        elif action == 'edit':
            await self.handle_edit_message(data)
        elif action == 'delete':
            await self.handle_delete_message(data)

    async def handle_new_message(self, data):
        message_content = data['message']
        sender_id = self.user.id

        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=self.other_user_id)
        
        # Проверяем, подключены ли оба пользователя и находятся ли они в одном чате
        if (
            sender_id in connected_users 
            and self.other_user_id in connected_users 
            and connected_users[sender_id]['room_group_name'] == self.room_group_name 
            and connected_users[self.other_user_id]['room_group_name'] == self.room_group_name
        ):
            is_read = True
        else:
            is_read = False

        message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message_content,
            is_read=is_read
        )

        timestamp = datetime.now().isoformat()

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
                'profile_icon': sender.profile_icon.url if sender.profile_icon else '/static/images/default-profile.png'
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

    async def chat_message(self, event):
        action = event['action']
        if action == 'new':
            message = event['message']
            sender = event['sender']
            sender_id = event['sender_id']
            timestamp = event['timestamp']
            profile_icon = event['profile_icon']

            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id'],
                'message': message,
                'sender': sender,
                'sender_id': sender_id,
                'timestamp': timestamp,
                'profile_icon': profile_icon
            }))
        elif action in ['edit', 'delete']:
            await self.send(text_data=json.dumps({
                'action': action,
                'message_id': event['message_id'],
                'message': event.get('message', '')
            }))