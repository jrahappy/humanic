from django.db import models
from accounts.models import CustomUser


class WebInquiry(models.Model):
    choices_status = [
        ("Inquiry", "Inquiry"),
        ("In Progress", "In Progress"),
        ("Closed", "Closed"),
    ]
    business_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    is_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=choices_status, default="Inquiry")

    def __str__(self):
        return f"Inquiry from {self.name} at {self.business_name}"

    class Meta:
        verbose_name = "Web Inquiry"
        verbose_name_plural = "Web Inquiries"
        ordering = ["-created_at"]


class WebBlog(models.Model):
    choice_status = [
        ("Draft", "Draft"),
        ("Published", "Published"),
        ("Archived", "Archived"),
    ]
    choice_category = [
        ("hr", "구인"),
        ("news", "소식"),
    ]
    category = models.CharField(max_length=20, choices=choice_category, default="hr")
    title = models.CharField(max_length=200)
    dept = models.CharField(max_length=30)
    from_date = models.DateField()
    to_date = models.DateField()
    status = models.CharField(max_length=20, choices=choice_status, default="Draft")
    content = models.TextField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# class WebBlogComment(models.Model):
#     blog = models.ForeignKey(WebBlog, on_delete=models.CASCADE, related_name="comments")
#     applicant = models.CharField(max_length=100)
#     phone = models.CharField(max_length=15, blank=True, null=True)
#     email = models.EmailField()
#     is_agreed = models.BooleanField(default=False)
#     attached_file = models.FileField(upload_to="blog_comments/", blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Comment by {self.applicant} on {self.blog}"
