
from django.contrib import admin
from .models import WebInquiry, WebBlog, WebBlogComment


@admin.register(WebInquiry)
class WebInquiryAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'name', 'position', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['business_name', 'name', 'email', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(WebBlog)
class WebBlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'dept', 'from_date', 'to_date', 'status', 'author', 'created_at']
    list_filter = ['category', 'status', 'created_at', 'from_date', 'to_date']
    search_fields = ['title', 'dept', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(WebBlogComment)
class WebBlogCommentAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'blog', 'email', 'is_agreed', 'created_at']
    list_filter = ['is_agreed', 'created_at']
    search_fields = ['applicant', 'email', 'blog__title']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
