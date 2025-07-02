import json
import os
from pathlib import Path
import environ
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from redis import Redis
from django.utils import timezone
from accounts.models import CustomUser
from chat.models import Group, Message
from django.core.exceptions import ObjectDoesNotExist
from redis.exceptions import ConnectionError as RedisConnectionError


# Environment setup (moved to a utility function for safety)
def get_env():
    env = environ.Env(DEBUG=(bool, False))
    BASE_DIR = Path(__file__).resolve().parent.parent
    try:
        environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
    except Exception as e:
        print(f"Failed to load .env: {e}")
    return env


class BaseChatConsumer(AsyncWebsocketConsumer):
    """Base class for shared chat functionality."""

    @database_sync_to_async
    def get_current_time(self):
        return timezone.now()

    @database_sync_to_async
    def update_presence(self, delta):
        env = get_env()
        try:
            redis = Redis.from_url(
                f"redis://:{env('REDIS_PASSWORD')}@{env('REDIS_URL')}"
            )
            key = f'presence:{self.scope["user"].id}'
            count = redis.incrby(key, delta)
            if count <= 0:
                redis.delete(key)
            redis.close()
            return count
        except (RedisConnectionError, KeyError) as e:
            print(f"Redis error in update_presence: {e}")
            return 0

    @database_sync_to_async
    def mark_read(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            message.read_by.add(self.scope["user"])
        except ObjectDoesNotExist:
            print(f"Message {message_id} not found")


class GroupChatConsumer(BaseChatConsumer):
    async def connect(self):
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.group_name = f"group_{self.group_id}"

        if await self.is_group_member():
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(
                f"User {self.scope['user'].username} connected to group {self.group_id}"
            )
            # Update presence count for the group
            await self.update_presence(1)
        else:
            await self.close(code=403)  # Unauthorized

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.update_presence(-1)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message")
            message_type = data.get("type")

            if message_type == "read":
                await self.mark_read(data["message_id"])
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "chat_message",
                        "message": f"Message {data['message_id']} read by {self.scope['user'].username}",
                        "sender": "system",
                        "timestamp": str(await self.get_current_time()),
                    },
                )
            elif message:
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
        except json.JSONDecodeError:
            print("Invalid JSON received")
            await self.send(text_data=json.dumps({"error": "Invalid message format"}))

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
        try:
            return Group.objects.filter(
                id=self.group_id, members=self.scope["user"]
            ).exists()
        except Exception as e:
            print(f"Error checking group membership: {e}")
            return False

    @database_sync_to_async
    def save_group_message(self, content):
        try:
            group = Group.objects.get(id=self.group_id)
            Message.objects.create(
                group=group, sender=self.scope["user"], content=content
            )
        except ObjectDoesNotExist:
            print(f"Group {self.group_id} not found")


class OneToOneChatConsumer(BaseChatConsumer):
    async def connect(self):
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]

        # Check if user is authenticated and has valid id
        if (
            self.scope["user"].is_anonymous
            or not hasattr(self.scope["user"], "id")
            or self.scope["user"].id is None
        ):
            print(
                f"Authentication failed: user={self.scope['user']}, id={getattr(self.scope['user'], 'id', None)}"
            )
            await self.close(code=403)
            return

        try:
            receiver_id_int = int(self.receiver_id)
            user_id = self.scope["user"].id

            # Ensure both IDs are valid integers
            if user_id is None:
                print(f"User ID is None for user: {self.scope['user']}")
                await self.close(code=403)
                return

            self.room_name = (
                f"chat_{min(user_id, receiver_id_int)}_{max(user_id, receiver_id_int)}"
            )

            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
            await self.update_presence(1)
            print(
                f"User {self.scope['user'].username} connected to room {self.room_name}"
            )

        except (ValueError, TypeError) as e:
            print(f"Invalid receiver_id or user_id: {e}")
            await self.close(code=400)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.update_presence(-1)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message")
            message_type = data.get("type")

            if message_type == "read":
                await self.mark_read(data["message_id"])
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        "type": "chat_message",
                        "message": f"Message {data['message_id']} read by {self.scope['user'].username}",
                        "sender": "system",
                        "timestamp": str(await self.get_current_time()),
                    },
                )
            elif message:
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
        except json.JSONDecodeError:
            print("Invalid JSON received")
            await self.send(text_data=json.dumps({"error": "Invalid message format"}))

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
        try:
            receiver = CustomUser.objects.get(id=self.receiver_id)
            Message.objects.create(
                sender=self.scope["user"], receiver=receiver, content=content
            )
        except ObjectDoesNotExist:
            print(f"User {self.receiver_id} not found")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope["url_route"]["kwargs"]["receiver_id"]
        self.user = self.scope["user"]

        if (
            self.user.is_anonymous
            or not hasattr(self.user, "id")
            or self.user.id is None
        ):
            print(f"Authentication failed for ChatConsumer: user={self.user}")
            await self.close(code=403)
            return

        try:
            receiver_id_int = int(self.receiver_id)
            user_id = self.user.id

            # Create a unique room name for the two users
            user_ids = sorted([user_id, receiver_id_int])
            self.room_name = f"chat_{user_ids[0]}_{user_ids[1]}"
            self.room_group_name = f"chat_{self.room_name}"

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(
                f"ChatConsumer: User {self.user.username} connected to room {self.room_name}"
            )

        except (ValueError, TypeError) as e:
            print(f"ChatConsumer error: {e}")
            await self.close(code=400)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Save message to database
        await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": self.user.username,
                "timestamp": str(timezone.now()),
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        timestamp = event["timestamp"]

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,
                    "timestamp": timestamp,
                }
            )
        )

    @database_sync_to_async
    def save_message(self, message):
        from django.utils import timezone

        receiver = CustomUser.objects.get(id=self.receiver_id)
        Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=message,
            timestamp=timezone.now(),
        )
