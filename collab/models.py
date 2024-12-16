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
    # 판독료
    readprice = models.IntegerField(default=0)
    # 협력판독료
    collab_price = models.IntegerField(default=0)
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


class ReferIllness(models.Model):
    refer = models.ForeignKey(Refers, on_delete=models.CASCADE)
    illness = models.ForeignKey("IllnessCode", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class ReferTreatment(models.Model):
    refer = models.ForeignKey(Refers, on_delete=models.CASCADE)
    treatment = models.ForeignKey("TreatmentCode", on_delete=models.CASCADE)
    readprice = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class ReferHistory(models.Model):
    refer = models.ForeignKey(Refers, on_delete=models.CASCADE)
    changed_status = models.CharField(max_length=20)
    memo = models.CharField(max_length=100)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class IllnessCode(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=250)
    eng_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.code + " - " + self.name


class TreatmentCode(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    eng_name = models.CharField(max_length=100, null=True, blank=True)
    point = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    deleted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.code + " - " + self.name
