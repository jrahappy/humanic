from django.forms import ModelForm
from .models import Post
from django.core.exceptions import ValidationError


class BlogForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "afile", "category"]

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise ValidationError("The title must be at least 5 characters long.")
        return title

    def clean_afile(self):
        afile = self.cleaned_data.get("afile")
        if afile:
            # You can validate the file type, size, etc.
            if afile.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("File size must be under 10MB.")
            if not afile.name.endswith((".png", ".jpg", ".jpeg", ".pdf")):
                raise ValidationError("Only PNG, JPG, JPEG, and PDF files are allowed.")
        return afile
