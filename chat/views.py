from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import Group, Message
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
        return redirect("login")  # Redirect to login if not authenticated

    staff = CustomUser.objects.get(id=staff_id)
    return render(
        request, "chat/partial/chat_window.html", {"user": user, "staff": staff}
    )


@login_required
def group_chat_view(request, group_id):
    group = Group.objects.get(id=group_id)
    if request.user not in group.members.all():
        return redirect("home")
    messages = group.group_messages.order_by("timestamp")[:50]
    return render(
        request,
        "group_chat.html",
        {
            "group": group,
            "messages": messages,
            "group_id": group_id,
            "chat_type": "group",
        },
    )


@login_required
def one_to_one_chat_view(request, receiver_id):
    receiver = CustomUser.objects.get(id=receiver_id)
    messages = (
        Message.objects.filter(sender=request.user, receiver=receiver)
        | Message.objects.filter(sender=receiver, receiver=request.user).order_by(
            "timestamp"
        )[:50]
    )
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


@login_required
def send_message(request):
    if request.method == "POST":
        content = request.POST.get("message")
        group_id = request.POST.get("group_id")
        receiver_id = request.POST.get("receiver_id")
        if group_id:
            group = Group.objects.get(id=group_id)
            if request.user in group.members.all():
                Message.objects.create(
                    group=group, sender=request.user, content=content
                )
        elif receiver_id:
            receiver = CustomUser.objects.get(id=receiver_id)
            Message.objects.create(
                sender=request.user, receiver=receiver, content=content
            )
        return render(
            request,
            "chat/partials/message.html",
            {"message": {"sender": request.user, "content": content}},
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
    group = Group.objects.get(id=group_id)
    group.members.add(request.user)
    return redirect("group_chat", group_id=group_id)


@login_required
def check_presence(request):
    redis = Redis.from_url(f"redis://:{env('REDIS_PASSWORD')}@{env('REDIS_URL')}")
    users = CustomUser.objects.all()
    presence = {u.id: redis.exists(f"presence:{u.id}") for u in users}
    return render(request, "partials/presence.html", {"presence": presence})
