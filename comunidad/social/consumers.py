import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import MensajeChat, MensajeChatComunidad, Comunidad
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
        print(f"User {self.user.username} connected to room {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"User {self.user.username} disconnected from room {self.room_name}")

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
            print(f"Message from {username}: {message}")
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
                print(f"Messages marked as read by {self.user.username}: {read_message_ids}")

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
        print(f"Marked messages as read: {read_message_ids}")
        return read_message_ids


class ChatComunidadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.comunidad_id = self.scope['url_route']['kwargs']['comunidad_id']
        self.room_group_name = f'chat_comunidad_{self.comunidad_id}'
        self.user = self.scope["user"]

        # Verificar si el usuario es miembro de la comunidad
        is_member = await self.is_community_member()
        if not is_member:
            await self.close()
            return

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
        message_type = data['type']
        if message_type == 'chat_message':
            message = data['message']
            username = data['username']
            mensaje = await self.save_message(username, message)
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
            await self.mark_messages_as_read()

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, username, message):
        user = User.objects.get(username=username)
        comunidad = Comunidad.objects.get(id=self.comunidad_id)
        return MensajeChatComunidad.objects.create(emisor=user, comunidad=comunidad, contenido=message)

    @sync_to_async
    def mark_messages_as_read(self):
        comunidad = Comunidad.objects.get(id=self.comunidad_id)
        unread_messages = MensajeChatComunidad.objects.filter(
            comunidad=comunidad
        ).exclude(leido_por=self.user)
        for message in unread_messages:
            message.marcar_como_leido(self.user)

    @sync_to_async
    def is_community_member(self):
        try:
            comunidad = Comunidad.objects.get(id=self.comunidad_id)
            return comunidad.miembros.filter(id=self.user.id).exists()
        except Comunidad.DoesNotExist:
            return False
