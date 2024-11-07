from django.db import models
from customer.models import Company
from accounts.models import CustomUser
from utils.base_func import (
    get_platform_choices,
    get_ayear_choices,
    get_amonth_choices,
    get_amodality_choices,
)
from django.core.validators import MinValueValidator, MaxValueValidator


def upload_to(instance, filename):
    return f"afiles/{instance.ayear}/{instance.amonth}/{filename}"


class UploadHistory(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    platform = models.CharField(max_length=10, choices=get_platform_choices, default="")
    ayear = models.CharField(max_length=4, choices=get_ayear_choices)
    amonth = models.CharField(max_length=2, choices=get_amonth_choices)
    description = models.TextField(null=True, blank=True)
    # afile = models.FileField(upload_to="afiles/")
    afile = models.FileField(upload_to=upload_to)
    imported = models.BooleanField(default=False)
    verified = models.BooleanField(default=False, null=True, blank=True)
    aggregated = models.BooleanField(default=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.name


class UploadHistoryTrack(models.Model):
    uploadhistory = models.ForeignKey(UploadHistory, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, null=True, blank=True)
    result = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return self.uploadhistory.name


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

    # 응급, 일반, 일응 3가지로 구분
    stat = models.CharField(max_length=100, null=True, blank=True)  # Emergency, Routine

    # 전체 판독료 매출액(병원이 지불하는 금액)
    readprice = models.FloatField(null=True, blank=True, default=0)

    # 일반적인 경우에는 병원이 지불하는 금액
    company_paid = models.FloatField(null=True, blank=True, default=0)

    # 휴먼에서 부담하기로 한 금액
    # 일반요청이 지연되어 휴먼에서 가산금을 부담하여 판독을 요청한 경우의 금액
    # STAT 칸의 '일응', 휴먼 칸의 "휴" 표시가 있는 경우에만 해당
    human_paid = models.FloatField(null=True, blank=True, default=0)

    reader = models.CharField(max_length=100, null=True, blank=True)
    approver = models.CharField(max_length=100, null=True, blank=True)

    # 판독의 성명
    radiologist = models.CharField(max_length=100, null=True, blank=True)
    # 판독의 ID(DBMS에서 자동부여)
    provider = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )  # provider
    studydate = models.CharField(max_length=100, null=True, blank=True)
    studydt = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    approveddttm = models.CharField(max_length=100, null=True, blank=True)
    approvedt = models.DateTimeField(null=True, blank=True)

    pacs = models.CharField(max_length=100, null=True, blank=True)
    requestdttm = models.CharField(max_length=100, null=True, blank=True)
    requestdt = models.DateTimeField(null=True, blank=True)

    ecode = models.CharField(max_length=100, null=True, blank=True)
    sid = models.CharField(max_length=100, null=True, blank=True)
    patientid = models.CharField(max_length=100, null=True, blank=True)
    human_paid_all = models.CharField(max_length=10, null=True, blank=True)
    is_human_paid = models.BooleanField(default=False)

    ayear = models.CharField(max_length=5, null=True, blank=True)
    amonth = models.CharField(max_length=2, null=True, blank=True)
    # 해당월의 마지막 날짜를 저장. 통계자료를 만들때 사용함(좀 더 생각해봄)
    # adate = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    time_to_complete = models.IntegerField(
        null=True, blank=True, default=0
    )  # 분단위로 기록함  approvaldt-requestdt

    verified = models.BooleanField(default=False)
    unverified_message = models.CharField(max_length=200, null=True, blank=True)
    excelrownum = models.IntegerField(null=True, blank=True, default=0)
    adjusted_price = models.FloatField(null=True, blank=True, default=0)
    is_onsite = models.BooleanField(default=False)  # Onsite 여부
    applied_rate = models.FloatField(
        null=True,
        blank=True,
        default=0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    pay_to_provider = models.FloatField(
        null=True, blank=True, default=0
    )  # 의사에게 최종지급할 금액
    pay_to_human = models.FloatField(
        null=True, blank=True, default=0
    )  # 병원에게 최종지급할 금액
    pay_to_service = models.FloatField(
        null=True, blank=True, default=0
    )  # 서비스사업자에게 최종지급할 금액

    is_emergency = models.BooleanField(default=False)  # 응급여부
    is_completed = models.BooleanField(default=False)  # 정산완료
    is_locked = models.BooleanField(default=False)  # 정산완료후 회계적으로 잠금처리
    is_human_outpatient = models.BooleanField(default=False)  # 외래여부
    is_take = models.BooleanField(default=False)  # 차감대상여부
    is_rework = models.BooleanField(
        default=False
    )  # 재작업여부(고객이 요청한 경우를 표시)

    def __str__(self):
        return self.case_id if self.case_id else "No Case ID"

    class Meta:
        db_table = "reportmaster"
        managed = True
        verbose_name = "reportmaster"


class ReportMasterStat(models.Model):
    UploadHistory = models.ForeignKey(UploadHistory, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="의사명"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name="병원명"
    )
    ayear = models.CharField("년도", max_length=4)
    amonth = models.CharField("월", max_length=2)
    # platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    amodality = models.CharField(
        "Modality", max_length=10, choices=get_amodality_choices
    )
    emergency = models.BooleanField(default=False)  # 응급여부
    human_outpatient = models.BooleanField(default=False)  # 휴먼외래여부
    give_or_take = models.BooleanField(default=False)  # False Give, True=take차감
    total_count = models.IntegerField(default=0)
    total_revenue = models.FloatField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ayear}-{self.amonth} {self.provider} {self.company} {self.amodality}"

    class Meta:
        db_table = "reportmasterstat"
        managed = True
        verbose_name = "reportmasterstat"


class ReportMasterPerformance(models.Model):
    provider = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="의사명"
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, verbose_name="병원명"
    )
    ayear = models.CharField("년도", max_length=4)
    amonth = models.CharField("월", max_length=2)
    amodality = models.CharField(
        "Modality", max_length=10, choices=get_amodality_choices
    )
    time_range = models.CharField("TimeRange", max_length=20)
    frequency = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class ReportMasterComment(models.Model):
    reportmaster = models.ForeignKey(ReportMaster, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class MagamMaster(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="작업자"
    )
    ayear = models.CharField("년도", max_length=4)
    amonth = models.CharField("월", max_length=2)
    target_rows = models.IntegerField(default=0)
    completed_rows = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # 정산과정을 모두 마친 상태
    is_completed = models.BooleanField(default=False)
    # 검증이 완료된 상태로 더 이상의 수정이 불가능한 상태로 만듬
    is_locked = models.BooleanField(default=False)
    # 판독의/병원 고객들의 접근을 통제하기 위한 상태
    is_opened = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ayear}-{self.amonth}"

    class Meta:
        db_table = "magammaster"
        managed = True
        verbose_name = "magammaster"


class MagamDetail(models.Model):
    magammaster = models.ForeignKey(
        MagamMaster, on_delete=models.CASCADE, verbose_name="마감"
    )
    humanrule = models.ForeignKey(
        "HumanRules", on_delete=models.CASCADE, verbose_name="규칙"
    )
    affected_rows = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)


class HumanRules(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    def_name = models.CharField(max_length=100)
    def_value = models.CharField(max_length=100)
    rules_order = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "rules"
        managed = True
        verbose_name = "rules"


class MagamAccounting(models.Model):
    ayear = models.CharField("년도", max_length=4)
    amonth = models.CharField("월", max_length=2)
    client = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="client",
        verbose_name="거래처",
        null=True,
        blank=True,
    )
    provider = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="provider",
        verbose_name="의사",
        null=True,
        blank=True,
    )
    account_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=50)
    account_memo = models.CharField(max_length=200)
    account_total = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
