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
    list_display = ("id", "group", "sender", "receiver", "content_preview", "timestamp")
    search_fields = ("content", "sender__username", "receiver__username")
    list_filter = ("group", "sender", "receiver", "timestamp")
    raw_id_fields = ("sender", "receiver")
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content"
