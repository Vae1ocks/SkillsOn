from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Chat, Message
from channels.db import database_sync_to_async


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.id = self.scope['url_route']['kwargs']['pk']
        self.room_group_name = f'chat_{self.id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.chat = await database_sync_to_async(Chat.objects.get)(id=self.id)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive_json(self, content):
        message = content['message']
        user = self.scope['user']
        
        if user.is_anonymous:
            return

        await database_sync_to_async(Message.objects.create)(
            chat=self.chat,
            text=message,
            user=user
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.first_name,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        await self.send_json({
            'message': message,
            'user': user
        })
