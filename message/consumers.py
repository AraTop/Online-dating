from channels.generic.websocket import AsyncWebsocketConsumer
import json
from users.models import User
from asgiref.sync import sync_to_async
from .models import Message  # Убедитесь, что импортируете модель сообщения
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_user_id = int(self.scope['url_route']['kwargs']['user_id'])  # Приведение к целому числу
        self.room_group_name = f'chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        sender_id = self.user.id

        sender = await sync_to_async(User.objects.get)(id=sender_id)
        receiver = await sync_to_async(User.objects.get)(id=self.other_user_id)

        # Сохранение сообщения в базе данных
        message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=message_content,
            is_read=False
        )
        timestamp = datetime.now().isoformat()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'sender': sender.first_name,
                'sender_id': sender.id,
                'timestamp': timestamp,
                'profile_icon': sender.profile_icon.url if sender.profile_icon else '/static/images/default-profile.png'
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        sender_id = event['sender_id']
        timestamp = event['timestamp']
        profile_icon = event['profile_icon']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'sender_id': sender_id,
            'timestamp': timestamp,
            'profile_icon': profile_icon
        }))