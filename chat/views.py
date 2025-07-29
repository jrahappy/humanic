from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Group, Message
from redis import Redis
import os
import environ
from pathlib import Path


def screen_capture(request):
    """
    A simple view to render a screen capture page.
    """
    return render(request, "chat/screen_capture.html")


def echo_page(request):
    """
    A simple view to test WebSocket echo functionality.
    """
    return render(request, "chat/echo_page.html")


@login_required
def index(request):
    user = request.user
    if not user.is_authenticated:
        return redirect("login")  # Redirect to login if not authenticated

    staffs = CustomUser.objects.filter(is_staff=True)
    return render(request, "chat/index.html", {"user": user, "staffs": staffs})


def chat_window(request, staff_id):
    user = request.user
    if not user.is_authenticated:
        return redirect("login")

    try:
        staff = CustomUser.objects.get(id=staff_id)
    except CustomUser.DoesNotExist:
        return redirect("chat:index")  # Redirect if staff not found

    return render(
        request, "chat/partials/chat_window.html", {"user": user, "staff": staff}
    )


@login_required
def group_chat_view(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        if request.user not in group.members.all():
            return redirect("chat:index")

        messages_list = group.group_messages.order_by("timestamp")
        paginator = Paginator(messages_list, 50)  # Show 50 messages per page
        page_number = request.GET.get("page", 1)
        messages = paginator.get_page(page_number)

        return render(
            request,
            "chat/group_chat.html",
            {
                "group": group,
                "messages": messages,
                "group_id": group_id,
                "chat_type": "group",
            },
        )
    except Group.DoesNotExist:
        return redirect("chat:index")


@login_required
def one_to_one_chat_view(request, receiver_id):
    try:
        receiver = CustomUser.objects.get(id=receiver_id)
        messages_list = (
            Message.objects.filter(sender=request.user, receiver=receiver)
            | Message.objects.filter(sender=receiver, receiver=request.user)
        ).order_by("timestamp")

        paginator = Paginator(messages_list, 50)  # Show 50 messages per page
        page_number = request.GET.get("page", 1)
        messages = paginator.get_page(page_number)

        return render(
            request,
            "chat/one_to_one_chat.html",
            {
                "receiver": receiver,
                "messages": messages,
                "receiver_id": receiver_id,
                "chat_type": "one_to_one",
            },
        )
    except CustomUser.DoesNotExist:
        return redirect("chat:index")


@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("message")
        group_id = request.POST.get("group_id")
        receiver_id = request.POST.get("receiver_id")
        timestamp = timezone.now()
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                if request.user in group.members.all():
                    Message.objects.create(
                        group=group,
                        sender=request.user,
                        content=content,
                        timestamp=timestamp,
                    )
            except Group.DoesNotExist:
                return redirect("chat:index")
        elif receiver_id:
            try:
                receiver = CustomUser.objects.get(id=receiver_id)
            except CustomUser.DoesNotExist:
                return redirect("chat:index")
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                timestamp=timestamp,
            )

            # Send message through WebSocket
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                import json

                channel_layer = get_channel_layer()

                # Create room name (same logic as in consumer)
                user_ids = sorted([request.user.id, int(receiver_id)])
                room_group_name = f"chat_chat_{user_ids[0]}_{user_ids[1]}"

                async_to_sync(channel_layer.group_send)(
                    room_group_name,
                    {
                        "type": "chat_message",
                        "message": content,
                        "sender": request.user.username,
                        "timestamp": timestamp.isoformat(),
                    },
                )
            except Exception as e:
                print(f"WebSocket send error: {e}")

        return render(
            request,
            "chat/partials/message.html",
            {
                "message": {
                    "sender": request.user,
                    "content": content,
                    "timestamp": timestamp,
                }
            },
        )
    return redirect("home")


@login_required
def create_group(request):
    if request.method == "POST":
        name = request.POST.get("name")
        group = Group.objects.create(name=name)
        group.members.add(request.user)
        return redirect("group_chat", group_id=group.id)
    return render(request, "create_group.html")


@login_required
def join_group(request, group_id):
    try:
        group = Group.objects.get(id=group_id)
        group.members.add(request.user)
        return redirect("chat:group_chat", group_id=group_id)
    except Group.DoesNotExist:
        return redirect("chat:index")


@login_required
def check_presence(request):
    try:
        redis = Redis.from_url(f"redis://:{env('REDIS_PASSWORD')}@{env('REDIS_URL')}")
        users = CustomUser.objects.all()
        presence = {u.id: redis.exists(f"presence:{u.id}") for u in users}
        redis.close()
    except (Exception, KeyError) as e:
        print(f"Redis connection error in check_presence: {e}")
        users = CustomUser.objects.all()
        presence = {u.id: False for u in users}  # Default to offline
    return render(request, "chat/partials/presence.html", {"presence": presence})
