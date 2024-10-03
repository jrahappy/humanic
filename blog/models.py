from django.db import models
from accounts.models import CustomUser, Profile


def upload_location(instance, filename):
    return f"blogfiles/{instance.author.username}/{filename}"


class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    afile = models.FileField(upload_to=upload_location, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
