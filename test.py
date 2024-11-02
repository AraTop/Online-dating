async def send_user_notification(self, sender_id):
        # Извлечение сообщения из базы данных с учетом обеих комбинаций sender и receiver
        message = await sync_to_async(
            lambda: Message.objects.filter(
                Q(receiver_id=sender_id) | 
                Q(sender_id=sender_id)
            ).first()
        )()

        if message:  # Проверяем, что сообщение действительно найдено
            print(f'Сообщение найдено {sender_id}')
            # Используем sync_to_async для получения receiver
            receiver = await sync_to_async(lambda: message.receiver)()

            await self.channel_layer.group_send(
                f'notifications_{receiver.id}',  # Группа для уведомлений
                {
                    'type': 'user_joined',
                    'action': 'user_joined',
                    'user_id': sender_id,  # ID первого пользователя
                }
            )
        else:
            print(f'Сообщение не найдено для sender_id: {sender_id}')