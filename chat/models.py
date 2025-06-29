from accounts.models import CustomUser
from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(CustomUser, related_name="chat_groups")
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="group_messages",
        null=True,
        blank=True,
    )
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="received_messages",
        null=True,
        blank=True,
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(CustomUser, related_name="read_messages")

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or 'group'} at {self.timestamp}"
