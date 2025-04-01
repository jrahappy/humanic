from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import CustomUser
from customer.models import Company
from utils.choices import OPPORTUNITY_STAGE, OPPORTUNITY_CATEGORY


# 병원고객들을 상담하는 곳임
class Opportunity(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="opportunities",
        null=True,
        blank=True,
    )
    agent = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="opportunities",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, help_text="Monthly Amount"
    )
    possibility = models.IntegerField(
        default=50,
        help_text="Percentage",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    target_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=20, choices=OPPORTUNITY_CATEGORY)
    stage = models.CharField(max_length=20, choices=OPPORTUNITY_STAGE)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.amount = round(self.amount, 2)
        super().save(*args, **kwargs)

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunites"

    def __str__(self):
        return f"{self.organization.business_name} - {self.amount}"


class Note(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="notes"
    )
    note = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.note


class Task(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="tasks"
    )
    task = models.TextField()
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return self.task


class OpportunityHistory(models.Model):
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="history"
    )
    stage = models.CharField(max_length=20, choices=OPPORTUNITY_STAGE)
    possibility = models.IntegerField(
        default=0,
        help_text="Percentage",
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Opportunity History"
        verbose_name_plural = "Opportunity Histories"

    def __str__(self):
        return self.stage


# 일반 환자들의 상담을 관리하는 테이블임
class Chance(models.Model):
    name = models.CharField(max_length=20)
    purpose = models.CharField(max_length=250)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    sns = models.CharField(max_length=100, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=OPPORTUNITY_STAGE)
    created_at = models.DateTimeField(auto_now_add=True)
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Chance"
        verbose_name_plural = "Chances"

    def __str__(self):
        return self.name


class ChanceComment(models.Model):
    chance = models.ForeignKey(Chance, on_delete=models.CASCADE, related_name="history")
    comment = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
