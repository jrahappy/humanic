from django.db import models
from accounts.models import CustomUser, Profile
from customer.models import Company


class Referral(models.Model):
    referral_source = models.CharField(max_length=50, null=True, blank=True)
    referral_code = models.CharField(max_length=10, null=True, blank=True)
    referred_by = models.CharField(max_length=50, null=True, blank=True)
    # 의뢰병원정보(referred_by를 이용해서 company를 찾아서 넣음)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    # 휴먼영상으로 일괄 저장
    referred_to = models.CharField(max_length=50, null=True, blank=True)
    requested_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    modality = models.CharField(max_length=50, null=True, blank=True)
    # modality를 코드화 시키는 것
    amodality = models.CharField(max_length=10, null=True, blank=True)
    bodypart = models.CharField(max_length=50, null=True, blank=True)
    # specialty를 코드화 시키는 것
    specialty2 = models.CharField(max_length=30, null=True, blank=True)
    case_id = models.CharField(max_length=50, null=True, blank=True)
    patient_name = models.CharField(max_length=50, null=True, blank=True)
    is_emergency = models.BooleanField(default=False)
    # 응급여부
    referral_status_from_source = models.CharField(
        max_length=50, null=True, blank=True
    )  # Referral status from source
    # 리퍼를 판독의들에게 배분하고 완료될때까지의 상태 관리
    referral_status_from_referdex = models.CharField(
        max_length=50, null=True, blank=True
    )
    # 판독의
    provider = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # 에이전트 아이디 저장
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.case_id


class ReferralComment(models.Model):
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment


class MatchRules(models.Model):
    provider = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    # all, not, default 값으로 구분 (all: 전담, not: 거부, default: 기본값)
    match_operator = models.CharField(max_length=10, null=True, blank=True)
    specialty2 = models.CharField(max_length=30, null=True, blank=True)
    amodality = models.CharField(max_length=10, null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True
    )
    bodypart = models.CharField(max_length=50, null=True, blank=True)
    memo = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.modality