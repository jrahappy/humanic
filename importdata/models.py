from django.db import models
from accounts.models import CustomUser
from customer.models import Company, Contract, ContractItem, Product, Platform


class EditedData(models.Model):
    apptitle = models.CharField(max_length=100, null=True, blank=True)
    case_id = models.CharField(max_length=100, null=True, blank=True)
    modality = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    approver = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class temp_doctor_table(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    specialty = models.CharField(max_length=50, null=True, blank=True)
    doctor_id = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    cv3_id = models.CharField(max_length=20, null=True, blank=True)
    onpacs_id = models.CharField(max_length=20, null=True, blank=True)
    department = models.CharField(max_length=20, null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    fee_rate = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class temp_customer_table(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    customer_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class importhistory(models.Model):
    SOURCES_FROM = {
        "ONPACS": "ONPACS",
        "CV3": "CV3",
        "HPACS": "HPACS",
        "ETC": "ETC",
    }
    AYEAR_CHOICES = {
        "2023": "2023",
        "2024": "2024",
        "2025": "2025",
        "2026": "2026",
    }
    AMONTH_CHOICES = {
        "01": "01",
        "02": "02",
        "03": "03",
        "04": "04",
        "05": "05",
        "06": "06",
        "07": "07",
        "08": "08",
        "09": "09",
        "10": "10",
        "11": "11",
        "12": "12",
    }
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    import_date = models.DateField(auto_now_add=True)
    source_from = models.CharField(
        max_length=10, choices=SOURCES_FROM, null=True, blank=True
    )
    ayear = models.CharField(max_length=5, choices=AYEAR_CHOICES, null=True, blank=True)
    amonth = models.CharField(
        max_length=5, choices=AMONTH_CHOICES, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="importdata/")
    created_at = models.DateTimeField(auto_now_add=True)
    imported = models.BooleanField(default=False)
    cleaned = models.BooleanField(default=False)

    def __str__(self):
        return self.file.name

    class Meta:
        db_table = "importhistory"
        managed = True
        verbose_name = "importhistory"
        verbose_name_plural = "importhistorys"


class rawdata(models.Model):
    importhistory = models.ForeignKey(importhistory, on_delete=models.CASCADE)
    apptitle = models.CharField(max_length=100, null=True, blank=True)
    case_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    bodypart = models.CharField(max_length=100, null=True, blank=True)
    modality = models.CharField(max_length=100, null=True, blank=True)
    equipment = models.CharField(max_length=100, null=True, blank=True)
    studydescription = models.CharField(max_length=100, null=True, blank=True)
    imagecount = models.IntegerField(null=True, blank=True)
    accessionnumber = models.CharField(max_length=100, null=True, blank=True)
    readprice = models.FloatField(null=True, blank=True)
    reader = models.CharField(max_length=100, null=True, blank=True)
    approver = models.CharField(max_length=100, null=True, blank=True)
    radiologist = models.CharField(max_length=100, null=True, blank=True)
    studydate = models.CharField(max_length=100, null=True, blank=True)
    approveddttm = models.CharField(max_length=100, null=True, blank=True)
    stat = models.CharField(max_length=100, null=True, blank=True)
    pacs = models.CharField(max_length=100, null=True, blank=True)
    requestdttm = models.CharField(max_length=100, null=True, blank=True)
    ecode = models.CharField(max_length=100, null=True, blank=True)
    sid = models.CharField(max_length=100, null=True, blank=True)
    patientid = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    cleaned = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    ayear = models.CharField(max_length=5, null=True, blank=True)
    amonth = models.CharField(max_length=5, null=True, blank=True)

    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "rawdata"
        managed = True
        verbose_name = "rawdata"
        verbose_name_plural = "rawdatas"


class cleanData(models.Model):
    rawdata = models.ForeignKey(rawdata, on_delete=models.CASCADE)  # rawdata
    apptitle = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # company

    case_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    bodypart = models.CharField(max_length=100)
    modality = models.CharField(max_length=100)
    equipment = models.CharField(max_length=100)
    studydescription = models.CharField(max_length=100, null=True, blank=True)
    imagecount = models.IntegerField(null=True, blank=True)
    accessionnumber = models.CharField(max_length=100, null=True, blank=True)
    stat = models.CharField(max_length=100, null=True, blank=True)  # Emergency, Routine

    readprice = models.FloatField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # product
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)  # contract
    contract_item = models.ForeignKey(
        ContractItem, on_delete=models.CASCADE
    )  # contract_item

    reader = models.CharField(max_length=100, null=True, blank=True)
    reader_clean = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="reader_id"
    )  # reader

    approver = models.CharField(max_length=100, null=True, blank=True)
    approver_clean = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="approver_id"
    )  # approver
    radiologist = models.CharField(max_length=100, null=True, blank=True)

    studydate = models.CharField(max_length=100, null=True, blank=True)
    studydate_clean = models.DateField(null=True, blank=True)

    approveddttm = models.CharField(max_length=100, null=True, blank=True)
    approveddttm_clean = models.DateTimeField(null=True, blank=True)  # approveddttm

    pacs = models.CharField(max_length=100, null=True, blank=True)
    Platform = models.ForeignKey(Platform, on_delete=models.CASCADE)  # platform

    requestdttm = models.CharField(max_length=100, null=True, blank=True)
    requestdttm_clean = models.DateTimeField(null=True, blank=True)  # requestdttm

    ecode = models.CharField(max_length=100, null=True, blank=True)
    sid = models.CharField(max_length=100, null=True, blank=True)
    patientid = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.case_id

    class Meta:
        db_table = "cleandata"
        managed = True
        verbose_name = "cleandata"
        verbose_name_plural = "cleandatas"
