import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get token from query string
        token = self.scope['query_string'].decode().split('=')[1] if b'token=' in self.scope['query_string'] else None
        
        if token:
            user = await self.get_user_from_token(token)
            if user:
                self.user = user
                self.room_group_name = f'user_{user.id}'
                
                # Join user-specific notification group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
                
                await self.accept()
                
                # Send connection success message
                await self.send(text_data=json.dumps({
                    'type': 'connection_established',
                    'message': 'Connected to notifications'
                }))
            else:
                await self.close()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        # Handle incoming WebSocket messages if needed
        pass
    
    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None