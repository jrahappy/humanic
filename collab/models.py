from django.db import models
from accounts.models import CustomUser, Profile
from customer.models import Company
from utils.base_func import GENDER, REFER_STATUS


class Refers(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    referred_date = models.DateField()
    patient_name = models.CharField(max_length=50)
    patient_gender = models.CharField(choices=GENDER, max_length=1)
    patient_birthdate = models.DateField()
    patient_phone = models.CharField(max_length=20, null=True, blank=True)
    # List 형태로 입력함
    illness = models.CharField(max_length=100, null=True, blank=True)
    # List 형태로 입력함
    treatment = models.CharField(max_length=100, null=True, blank=True)
    # 임상의견(의뢰인이 입력함)
    opinion1 = models.TextField()
    status = models.CharField(choices=REFER_STATUS, max_length=20)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 아래는 진효 회송서 정보
    chart_number = models.CharField(max_length=20, null=True, blank=True)
    manage_number = models.CharField(max_length=20, null=True, blank=True)
    provider = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    illness2 = models.CharField(max_length=100, null=True, blank=True)
    opinion2 = models.TextField(null=True, blank=True)
    opinioned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # return self.company.business_name + " - " + self.patient_name
        return self.company.business_name + " - " + self.patient_name


class ReferHistory(models.Model):
    refer = models.ForeignKey(Refers, on_delete=models.CASCADE)
    changed_status = models.CharField(max_length=20)
    memo = models.CharField(max_length=100)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
