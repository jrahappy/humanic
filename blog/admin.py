from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from django.utils.html import format_html
from .models import Post, PostAttachment


class PostAttachmentInline(admin.TabularInline):
    model = PostAttachment
    extra = 1
    fields = ['file', 'get_file_size']
    readonly_fields = ['get_file_size']
    
    def get_file_size(self, obj):
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "N/A"
    get_file_size.short_description = 'File Size'


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['title', 'get_category_display', 'author', 'get_status', 'has_file', 'created_at']
    list_filter = ['is_public', 'category', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username', 'author__email']
    readonly_fields = ['created_at', 'deleted_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 20
    inlines = [PostAttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'author', 'is_public')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('File Attachment', {
            'fields': ('afile',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    get_category_display.short_description = 'Category'
    get_category_display.admin_order_field = 'category'
    
    def has_file(self, obj):
        return bool(obj.afile)
    has_file.boolean = True
    has_file.short_description = 'Has File'
    
    def get_status(self, obj):
        if obj.is_public:
            return format_html('<span style="color: green;">●</span> Public')
        else:
            return format_html('<span style="color: orange;">●</span> Private')
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'is_public'
    
    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }


@admin.register(PostAttachment)
class PostAttachmentAdmin(admin.ModelAdmin):
    list_display = ['get_post_title', 'file', 'get_file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title']
    raw_id_fields = ['post']
    readonly_fields = ['created_at', 'get_file_size']
    ordering = ['-created_at']
    list_per_page = 20
    
    def get_post_title(self, obj):
        return obj.post.title
    get_post_title.short_description = 'Post'
    get_post_title.admin_order_field = 'post__title'
    
    def get_file_size(self, obj):
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "N/A"
    get_file_size.short_description = 'File Size'
