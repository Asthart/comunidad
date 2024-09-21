import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import MensajeChat
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.mark_messages_as_read()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        if message_type == 'chat_message':
            message = data['message']
            username = data['username']
            mensaje = await self.save_message(username, self.room_name, message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'fecha_envio': mensaje.fecha_envio.isoformat(),
                    'id': mensaje.id,
                }
            )
        elif message_type == 'mark_as_read':
            read_message_ids = await self.mark_messages_as_read()
            if read_message_ids:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'messages_marked_as_read',
                        'message_ids': read_message_ids,
                        'reader': self.user.username,
                        'fecha_lectura': timezone.now().isoformat(),
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def messages_marked_as_read(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, username, room_name, message):
        user = User.objects.get(username=username)
        return MensajeChat.objects.create(emisor=user, room_name=room_name, contenido=message)

    @sync_to_async
    def mark_messages_as_read(self):
        room_name_parts = self.room_name.split('_')
        other_user_id = room_name_parts[1] if int(room_name_parts[0]) == self.user.id else room_name_parts[0]
        other_user = User.objects.get(id=other_user_id)
        unread_messages = MensajeChat.objects.filter(
            room_name=self.room_name,
            emisor=other_user,
            leido=False
        )
        read_message_ids = []
        for message in unread_messages:
            message.leido = True
            message.fecha_lectura = timezone.now()
            message.save()
            read_message_ids.append(message.id)
        return read_message_ids
