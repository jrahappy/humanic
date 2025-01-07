from django.db import models
from accounts.models import CustomUser, Profile
from customer.models import Company
from utils.base_func import GENDER, REFER_STATUS


class Refers(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    # 의뢰하는 의사명
    refer_doctor = models.CharField(max_length=50, null=True, blank=True)
    referred_date = models.DateField(null=True, blank=True)
    patient_name = models.CharField(max_length=50)
    patient_gender = models.CharField(choices=GENDER, max_length=1)
    patient_birthdate = models.DateField(null=True, blank=True)
    patient_phone = models.CharField(max_length=20, null=True, blank=True)
    # List 형태로 입력함
    illness = models.CharField(max_length=100, null=True, blank=True)
    # List 형태로 입력함
    treatment = models.CharField(max_length=100, null=True, blank=True)
    # 판독료
    readprice = models.IntegerField(default=0, null=True, blank=True)
    # 협력판독료
    collab_price = models.IntegerField(default=0, null=True, blank=True)
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
    cosigned_at = models.DateTimeField(null=True, blank=True)
    # url = models.URLField(null=True, blank=True)
    url = models.CharField(max_length=1024, null=True, blank=True)
    # webpacs_url = models.TextField(null=True, blank=True)

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


class ReferSimpleDiagnosis(models.Model):
    refer = models.ForeignKey(Refers, on_delete=models.CASCADE)
    diagnosis = models.ForeignKey("SimpleDiagnosis", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " - ".join(
            filter(
                None,
                [
                    self.diagnosis.code1,
                    self.diagnosis.code2,
                    self.diagnosis.code3,
                    self.diagnosis.code4,
                ],
            )
        )


class ReferHistory(models.Model):
    refer = models.ForeignKey(Refers, on_delete=models.CASCADE)
    changed_status = models.CharField(max_length=20)
    memo = models.CharField(max_length=100)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.refer.patient_name + " - " + self.changed_status + " - " + self.memo


class IllnessCode(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=250)
    eng_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.code + " - " + self.name

    class Meta:
        verbose_name = "질병코드"
        verbose_name_plural = "질병코드"
        ordering = ["code"]


class MyIllnessCode(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    illness_code = models.ForeignKey(IllnessCode, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.illness_code.code + " - " + self.illness_code.name

    class Meta:
        ordering = ["illness_code__code"]


# 2021/12/26 : 실제 병원에서 처리를 한 것들을 저장하는 테이블임. 현재는 사용되지 않음.
class TreatmentCode(models.Model):
    code = models.CharField(max_length=10)
    category1 = models.CharField(max_length=100, null=True, blank=True)
    category2 = models.CharField(max_length=100, null=True, blank=True)
    category3 = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    eng_name = models.CharField(max_length=100, null=True, blank=True)
    point = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    deleted_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.code + " - " + self.name

    class Meta:
        verbose_name = "행위코드"
        verbose_name_plural = "행위코드"
        ordering = ["code"]


class SimpleDiagnosis(models.Model):
    code1 = models.CharField(max_length=100, null=True, blank=True)
    code2 = models.CharField(max_length=200, null=True, blank=True)
    code3 = models.CharField(max_length=100, null=True, blank=True)
    code4 = models.CharField(max_length=100, null=True, blank=True)
    order = models.IntegerField(default=0)
    step = models.SmallIntegerField(default=0)
    is_head = models.BooleanField(default=False)
    short_name = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        # return self.code1 + " - " + self.code2 + " - " + self.code3 + " - " + self.code4
        return " - ".join(
            filter(None, [self.code1, self.code2, self.code3, self.code4])
        )

    class Meta:
        verbose_name = "간단진단"
        verbose_name_plural = "간단진단"
        ordering = ["order"]


class MySimpleDiagnosis(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    simple_diagnosis = models.ForeignKey(SimpleDiagnosis, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " - ".join(
            filter(
                None,
                [
                    self.simple_diagnosis.code1,
                    self.simple_diagnosis.code2,
                    self.simple_diagnosis.code3,
                    self.simple_diagnosis.code4,
                ],
            )
        )

    class Meta:
        ordering = ["simple_diagnosis__order"]


class ReferFile(models.Model):
    def upload_location_refer(instance, filename):
        return f"refer_files/{instance.refer.id}/{filename}"

    refer = models.ForeignKey(Refers, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(
        upload_to=upload_location_refer, max_length=250, null=True, blank=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Refer File"
        verbose_name_plural = "Refer Files"

    def __str__(self):
        return self.file.name
