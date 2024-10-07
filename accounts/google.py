from google.cloud import recaptchaenterprise_v1
from google.cloud.recaptchaenterprise_v1 import Assessment

project_id = "6LfsGVoqAAAAAJnfBtNPorl1YmAReX2BqBaMY8c-"


def create_assessment(
    project_id: str, recaptcha_key: str, token: str, recaptcha_action: str
) -> Assessment:
    """UI 작업의 위험을 분석하는 평가를 만듭니다.
    Args:
        project_id: Google Cloud 프로젝트 ID입니다.
        recaptcha_key: 사이트/앱과 연결된 reCAPTCHA 키입니다.
        token: 클라이언트에서 가져온 생성된 토큰입니다.
        recaptcha_action: 토큰에 해당하는 작업 이름입니다.
    """

    client = recaptchaenterprise_v1.RecaptchaEnterpriseServiceClient()

    # 추적할 이벤트의 속성을 설정합니다.
    event = recaptchaenterprise_v1.Event()
    event.site_key = recaptcha_key
    event.token = token

    assessment = recaptchaenterprise_v1.Assessment()
    assessment.event = event

    project_name = f"projects/{project_id}"

    # 평가 요청을 작성합니다.
    request = recaptchaenterprise_v1.CreateAssessmentRequest()
    request.assessment = assessment
    request.parent = project_name

    response = client.create_assessment(request)

    # 토큰이 유효한지 확인합니다.
    if not response.token_properties.valid:
        print(
            "The CreateAssessment call failed because the token was "
            + "invalid for the following reasons: "
            + str(response.token_properties.invalid_reason)
        )
        return

    # 예상한 작업이 실행되었는지 확인합니다.
    if response.token_properties.action != recaptcha_action:
        print(
            "The action attribute in your reCAPTCHA tag does"
            + "not match the action you are expecting to score"
        )
        return
    else:
        # 위험 점수와 이유를 가져옵니다.
        # 평가 해석에 대한 자세한 내용은 다음을 참조하세요.
        # https://cloud.google.com/recaptcha-enterprise/docs/interpret-assessment
        for reason in response.risk_analysis.reasons:
            print(reason)
        print(
            "The reCAPTCHA score for this token is: "
            + str(response.risk_analysis.score)
        )
        # 평가 이름(ID)을 가져옵니다. 평가에 주석을 추가하는 데 사용합니다.
        assessment_name = client.parse_assessment_path(response.name).get("assessment")
        print(f"Assessment name: {assessment_name}")
    return response
