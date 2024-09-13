from django.db import models
from customer.models import Company, Platform
from accounts.models import CustomUser, Profile
from utils.base_func import (
    get_platform_choices,
    get_ayear_choices,
    get_amonth_choices,
    get_amodality_choices,
)


class UploadHistory(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    platform = models.CharField(max_length=10, choices=get_platform_choices, default="")
    ayear = models.CharField(max_length=4, choices=get_ayear_choices)
    amonth = models.CharField(max_length=2, choices=get_amonth_choices)
    description = models.TextField(null=True, blank=True)
    afile = models.FileField(upload_to="afiles/")
    imported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Create your models here.
class ReportMaster(models.Model):
    uploadhistory = models.ForeignKey(
        UploadHistory, on_delete=models.CASCADE, null=True, blank=True
    )
    apptitle = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True
    )  # company

    case_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    bodypart = models.CharField(max_length=100, null=True, blank=True)
    modality = models.CharField(max_length=100, null=True, blank=True)
    equipment = models.CharField(max_length=100, null=True, blank=True)
    amodality = models.CharField(
        max_length=10, choices=get_amodality_choices, null=True, blank=True
    )
    studydescription = models.CharField(max_length=100, null=True, blank=True)
    imagecount = models.IntegerField(null=True, blank=True, default=0)
    accessionnumber = models.CharField(max_length=100, null=True, blank=True)
    stat = models.CharField(max_length=100, null=True, blank=True)  # Emergency, Routine

    readprice = models.FloatField(null=True, blank=True, default=0)
    reader = models.CharField(max_length=100, null=True, blank=True)
    approver = models.CharField(max_length=100, null=True, blank=True)
    radiologist = models.CharField(max_length=100, null=True, blank=True)
    provider = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )  # provider
    studydate = models.CharField(max_length=100, null=True, blank=True)
    studydt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    approveddttm = models.CharField(max_length=100, null=True, blank=True)
    approvedt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    pacs = models.CharField(max_length=100, null=True, blank=True)
    platform = models.CharField(
        max_length=20, choices=get_platform_choices, null=True, blank=True
    )
    requestdttm = models.CharField(max_length=100, null=True, blank=True)
    requestdt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    ecode = models.CharField(max_length=100, null=True, blank=True)
    sid = models.CharField(max_length=100, null=True, blank=True)
    patientid = models.CharField(max_length=100, null=True, blank=True)

    ayear = models.CharField(max_length=5, null=True, blank=True)
    amonth = models.CharField(max_length=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "reportmaster"
        managed = True
        verbose_name = "reportmaster"
