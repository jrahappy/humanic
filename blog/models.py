from django.db import models
from accounts.models import CustomUser, Profile
from utils.base_func import get_blog_category


def upload_location(instance, filename):
    return f"blogfiles/{instance.author.username}/{filename}"


class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=get_blog_category, default="1")
    title = models.CharField(max_length=200, help_text="200 characters max")
    content = models.TextField(null=True, blank=True)
    afile = models.FileField(upload_to=upload_location, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
