from django.db import models
from accounts.models import CustomUser
from customer.models import Company
from utils.base_func import TASK_STATUS
from django.core.validators import MinValueValidator, MaxValueValidator


class Task(models.Model):
    agent = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks_as_agent",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TASK_STATUS, default="Todo")
    start_time = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    opinion = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tasks_created"
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title

    def clean(self):
        if self.due_date and self.start_time and self.due_date < self.start_time:
            raise ValidationError("Due date cannot be earlier than start time.")

    def get_absolute_url(self):
        return reverse("task_detail", kwargs={"pk": self.pk})


class TaskFiles(models.Model):
    def upload_location(instance, filename):
        return f"task_files/{instance.task.id}/{filename}"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(
        upload_to=upload_location, max_length=250, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Task File"
        verbose_name_plural = "Task Files"

    def __str__(self):
        return self.file.name


class Project(models.Model):
    owner = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=TASK_STATUS, default="Todo")
    start_doing_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    opinion = models.TextField(null=True, blank=True)
    progress = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="0-100",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="created_by_project"
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title


class ProjectTask(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_tasks"
    )
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="project_tasks"
    )
    order = models.IntegerField(default=0)
    depth = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Project Task"
        verbose_name_plural = "Project Tasks"
