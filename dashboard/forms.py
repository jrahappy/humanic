from django import forms
from .models import Blog
from allauth.account.forms import ChangePasswordForm


class blogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = "__all__"
        exclude = ["author", "created_at", "updated_at"]
