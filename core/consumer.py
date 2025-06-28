from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from accounts.models import CustomUser
from chat.models import Group, Message
from django.utils import timezone
from redis import Redis

import os
import environ
from pathlib import Path

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.group_name = f"group_{self.group_id}"

        if await self.is_group_member():
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.update_presence(1)
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.update_presence(-1)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        if data.get("type") == "read":
            await self.mark_read(data["message_id"])

        await self.save_group_message(message)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.scope["user"].username,
                "timestamp": str(await self.get_current_time()),
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def is_group_member(self):
        return Group.objects.filter(
            id=self.group_id, members=self.scope["user"]
        ).exists()

    @database_sync_to_async
    def save_group_message(self, content):
        group = Group.objects.get(id=self.group_id)
        Message.objects.create(group=group, sender=self.scope["user"], content=content)

    @database_sync_to_async
    def get_current_time(self):
        from django.utils import timezone

        return timezone.now()

    @database_sync_to_async
    def update_presence(self, delta):
        from redis import Redis

        redis = Redis.from_url(f"redis://:{env('REDIS_PASSWORD')}@{env('REDIS_URL')}")
        key = f'presence:{self.scope["user"].id}'
        count = redis.incrby(key, delta)
        if count <= 0:
            redis.delete(key)
        return count

    @database_sync_to_async
    def mark_read(self, message_id):
        message = Message.objects.get(id=message_id)
        message.read_by.add(self.scope["user"])


class OneToOneChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]
        self.room_name = f'chat_{min(self.scope["user"].id, int(self.receiver_id))}_{max(self.scope["user"].id, int(self.receiver_id))}'

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.update_presence(1)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.update_presence(-1)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        if data.get("type") == "read":
            await self.mark_read(data["message_id"])

        await self.save_one_to_one_message(message)

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.scope["user"].username,
                "timestamp": str(await self.get_current_time()),
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    @database_sync_to_async
    def save_one_to_one_message(self, content):
        receiver = CustomUser.objects.get(id=self.receiver_id)
        Message.objects.create(
            sender=self.scope["user"], receiver=receiver, content=content
        )

    @database_sync_to_async
    def get_current_time(self):

        return timezone.now()

    @database_sync_to_async
    def update_presence(self, delta):
        from redis import Redis

        redis = Redis.from_url(f"redis://:{env('REDIS_PASSWORD')}@{env('REDIS_URL')}")
        key = f'presence:{self.scope["user"].id}'
        count = redis.incrby(key, delta)
        if count <= 0:
            redis.delete(key)
        return count

    @database_sync_to_async
    def mark_read(self, message_id):
        message = Message.objects.get(id=message_id)
        message.read_by.add(self.scope["user"])


# Note: The OneToOneChatConsumer assumes that the Message model has a 'receiver' field.
# If it does not, you will need to adjust the model and the save method accordingly.
# Also, ensure that the routing for this consumer is set up correctly in your routing.py file.
