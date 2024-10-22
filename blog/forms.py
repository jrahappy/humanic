from django.forms import ModelForm, modelformset_factory
from django import forms
from .models import Post, PostAttachment
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


class PostForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea)
    files = forms.FileField()  # Use FileField normally
    is_public = forms.BooleanField(required=False)

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise forms.ValidationError("The title must be at least 5 characters long.")
        return title
