from django.db import models
from accounts.models import CustomUser, Profile
from utils.base_func import get_blog_category
from ckeditor.fields import RichTextField


def upload_location(instance, filename):
    return f"blogfiles/{instance.author.username}/{filename}"


def upload_location_public(instance, filename):
    return f"blogfiles/{instance.post.id}/{filename}"


class Post(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    category = models.CharField(max_length=50, choices=get_blog_category, default="1")
    title = models.CharField(max_length=200, help_text="200 characters max")
    # content = models.TextField(null=True, blank=True)
    content = RichTextField(null=True, blank=True)
    afile = models.FileField(upload_to=upload_location, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class PostAttachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_location_public)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title
