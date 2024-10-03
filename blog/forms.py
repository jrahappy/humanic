from django.forms import ModelForm
from .models import Post


class BlogForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "afile"]
