from django.contrib import admin
from .models import Group, Message


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    filter_horizontal = ("members",)

    def get_form(self, request, obj=None, **kwargs):
        """Override to ensure proper form context."""
        form = super().get_form(request, obj, **kwargs)
        return form

    def get_fieldsets(self, request, obj=None):
        """Override to ensure proper fieldset handling."""
        return super().get_fieldsets(request, obj)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "sender", "content", "timestamp")
    search_fields = ("content",)
    list_filter = ("group", "sender", "timestamp")
