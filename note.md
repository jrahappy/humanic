- AWS Lightsail setting : Done
- AWS PostgreSQL setting : Done
- Ubuntu server update : Done
- .env Setting : Done
- S3 Bucket setting : not use
- Git setting : Done
- Basic migration from Excel file : Done
- Domain name : humanrad.com


-Issue: Done
    - Tailwindcss Setting issue: Done
        ** Static folder를 static/css/dist/styles.css 에 복사해둠
        ** STATIC_ROOT, STATIC_URL, STATICFILES_DIRS 세팅에 대해서 공부함
        ** Nginx  에서 서비스 파일을 볼 때에 static/ 관련 부분에 대해서 함부로 변경하지 않아야함
    - Data duplication issue 와 새 닥터들 등록 필요       
        
        "민훈"	294
        "고지영"	53
        "김세우"	522
        "김여군"	356
        "김종열"	34
        "최현수"	348
        "김수진
        (유방)"	2976
        "김수진
        (신경두경부)"	189

## Celery Setup ##
    - 데이터 처리(클리닝, Primary Key 잡아주는 로직)를 진행할 때에 많은 시간이 소요되므로 분산처리가 반드시 필요함
    - Redis 를 Messaging Broker 로 사용하기로 하고 redis.com 에서 유료 구입함. 추후 AWS에서 제공하는 Broker 사용도 고려함
    - RabbitMQ 도 고려함.
    
## Rule 4-1 : - 일반촬영 판독단가 1,333원 이하 건 → 1,000원 조정 
    - SELECT * FROM public.reportmaster WHERE readprice<1333 and amodality='CR'. update adjusted_price=1000;

## Rule 4-2 : - Chest CT(비조영) 판독단가 19,600원 이하 건 → 14,700원 조정
    - SELECT * FROM public.reportmaster WHERE (readprice<19600 and amodality='CT' and bodypart='CHEST').update adjusted_price=14700;

## Rule 4-3 : - MR 판독단가 40,000원 미만 건 → 71% 조정 (수수료율 구분없이 전체)
    - SELECT * FROM public.reportmaster WHERE (readprice<40000 and amodality='MR').update applied_rate=0.71;

## Rule 5 : 나머지는 판독의 수수료율에 따라 계산함
    - 4번 항목의 Case들은 제외, PACS=ONSITE 경우 제외한 나머지에 적용함
    - Case 의 Modality, readprice 확인
    - Case 판독의, Modality 수수료율 확인
    - Case readyprice x 수수료율 => pay_to_doctor 에 넣고 is_complete=True


## Rule 6 : 서울보라매, 일산병원외 ONSITE 공제수수료 계산
    - pace=ONSITE 경우에는 (1-판독의 지급수수료율) X readprice X -1로 하여  pay_to_doctor 에 넣고 is_complete=True


## 매월 신규 추가되는 병원들을 정규화 작업전에 미리 확인해서 일괄 넣는 단계가 필요.
    송파미소병원(tele)(SCU) 과 송파미소병원
    열린의료재단서교의원

ht-get="{% url 'report:report_period_month_radiologist' ayear amonth rpm.provider %}"

## 플랫폼 등록
테크하임 : 김내과의원이 유비에도 동명이 있음.
동울산영상의학과의원은 : INFINTT AND ES헬스케어에도 등록되어 있음

## 플랫폼 커미션 지급 ##
고객병원에 따라 영업(5%), PACS(5%), 원격판독시스템(5%) 최대 15까지 가능
적용은 일단 고객병원별 월별로 집계를 낸 후에 해당 병원의 영업, PACS, 원격판독 시스템 정보를 가지고 별도의 수수료 지급테이블에 넣는 것이 좋을 것 같음

## onsite 관련 처리 ##
일산368, 보라매87 파일로 올라온 것만 차감률 적용함
그 외 해당 병원에 판독한 건들은 정상계산(아래는 해당 의사들 목록임)

 
## 화상회의 09/25/2024 ##

  손경선 kasia71@humic.co.kr
  이종엽 yuphim@humic.co.kr

    ** 개선해야할 부분
    1. 휴먼외래와 전체 판독료를 분리해서 합산해서 보여주야 함.
    2. 동명 2인... 김혜진 145
    3. 동명이인의 경우에 정확성을 기하기 위해 Approver 로 구분함.
    4. 판독의 검색이 쉽게 함.

    문제점 : 
     CR, CT 가격이 너무 낮은 경우는 휴먼외래에도 적용되는지? -> 휴먼외래는 무조건 닥터 100%
     CTROW 이슈 Chest CT(비조영) 판독단가 19,600원 이하 건 → 14,700원 조정.. 어떻게 아는지.. 

## 09/27/2024 ##
    
    - Rule: 휴먼외래 건들에 대한 US, XA, FR 건 판독료 지급 제외 Rule 완료 
    - Rule: 대표원장단(김성현, 이재희) 판독료 계산 처리 완료
    - 개별 의사별 판독표 재계산 함수 완료
    
    => 모든 의사별 판독료 계산 완료
    
## 09/29/2024 ##
    - bodypart 의 정규화 방안 검토
    - 병원은 사업자번호, 판독의는 면허번호 추가 검토

    - 2hrs 이내(온사이트와 원격은 나눠야함), 1d, 2d, 7d, 그 이상 
    - Assign 은 시점이 중요하긴 함. 현재는 엑셀에는 없어서.. 추후 고민함.

## 10/01/2024 ##
    - 서비스 업체들 등록 중
    - 김내과의원(ES, 테크하임, HH)
    

## 10/21/2024 ##
    - 계정 생성: 아이디는 이메일 이름으로 함.
        -> 김성현, 이종엽, 박종성 팀장, 송경선 팀장
    - 일응(보라매) 
    - 판독 시간 계산 (고민필요)
        - 주말, 공휴일 제외
        - 평일도 오후 6시 이후 접수는 익일 9시부터 계산
        - 응급:
            - 들어와서 2시간이내, 4시간이내
            - 토요일 9-13시까지만 받음
            - 일요일 공휴일은 안받고 다음 일하는 날 9시부터 적용함
    
## 10/24/2024 
    - 원단위 이하 적용 방법 정의
        -> 홀수로 나눌 때에 발생되는 문제임.
        -> 발생시점은 주로 판독의 지급률 적용할 때에 발생함
        -> 발생 후 즉시 원단위 이하는 버리는 것으로 함.
        -> Python의 Float-limitation error 가 있음. 원단위 이하는 모두 라운드업해야 함.

    - 휴(human_paid_all 필드)
        -> 이 건은 무조건 readprice 의 금액이 human_paid 칸으로 옴겨져야 함.
        -> 즉 현재 ReportMaster에서 readprice 외에 company_paid와 human_paid 필드를 추가해야 함. Done
        -> 일반 경우에는 모두 readprice가 company_paid와 와 같음
        -> 휴의 경우에는 human_paid에 readprice가 와야 함.
        -> 휴와 일응은 동시에 적용되지 않음
        -> 검증예. 임지연/경북대 박태호 환자케이스
        803841	"경북대학교병원"	"박태호"	"9"	21000	"임지연"	"2024"	"9"	"CT"		"휴"	true	21000	21000	0	0.7	22049.999999999996	-1049.9999999999982

    - 일응(stat 필드)
        -> 일응은 병원은 일반의뢰 적용, 판독의에게는 응급판독 적용된 경우임
        -> 일응은 50% 가산 응급부담을 human_paid 칸에 넣음
        -> 검증예. 
        637023	"국민건강보험공단일산병원"	"L*E*M*N*S*K"	"9"	48000	"김혜진"	"2024"	"9"	"MR"	"일응"		false	48000	48000	0	0.75	-12000	12000
        637023	"국민건강보험공단일산병원"	"L*E*M*N*S*K"	"9"	48000	"김혜진"	"2024"	"9"	"MR"	"일응"		false	48000	48000	24000	0.75	-18000	18000
        
        첫번째 계산
            병원부담: 48000
            닥터 기수령: 36000 (0.75)
            휴먼 차감: -12000 (닥터 실수령: 36000-12000=24000)
        두번째 계산:
            일응추가: 24000
            닥터 일응수령: 18,000
            휴먼 수수료: 6000
        => 결과: 
            pay_to_provider = 기존 휴먼 차감 -12000 에 일용 수당 18000을 더한 6000을 지급함
            휴먼은 당초 수입 12000 일용 수입 6000으로 총 18000원이고 일용지출 -24000 이 발생되어 결과적으로 총 -6000원의 손해가 발생됨. 기회비용까지 감안하면 +12000 에서 -18000이 되었으니 총 -6000원이 손해이다.

    - 소요 시간 계산

        20241022 미팅 내용용

            일산병원, 보라매병원
            응급판독 처리
            병원에서는 일반처리 판독의는 응급으로 대응한 건
            지금 정리하고 있는 Table에는 일응 (일반응급)
            계정생성
            병원에는 청구못하는 데 판독의에게 100%지급해야 할것
            신규컬럼(휴먼)에  “휴”로 입력한다.

            48시 이내 판독조건에는 휴일, 공휴일 제외

            9시 부터 18시 까지 업로드 시간 계산

            18시 이후 업로드된 Case는 다음날 오전 9시로 계산

            응급판독의뢰
            2시간 이내
            4시간 이내

            토요일응급판독 9시 ~ 13시 까지 받고 있음.

            Unknown은 양지병원 원내판독 홍새롬 판독의 일반판독

# 10/28/2024 
    - Python Float 에러에 대해서 Rule에 CEIL 을 수행하도록 해야 함. 현재는 PostgreSQL에서 한 번에 처리했으나 추후에는 Cleaning 혹은 Import 과정에서 처리하는 것이 좋겠음(추가 검증 필요)


# 11/01/2024 
    - CRM 기능 추가 고민함
        - Company 입력/수정 부분이 더 보강되어야 함. 
        - Comments, Trackings, 영업단계별 진행 상태에 대한 정보를 정의해야 함.
        
        
    
# 11/9/204 
    - 의사별(사용자) 업무시간, 휴일 등록 기능 완료
# 11/10/2024
    - 리퍼체크 리스트 검토
    - 예
        "강미진 월-금 일7건(추가X)
        21/11/04→리퍼건이 없을 떄는 없다고 메일안내 요청주심 //동산의료원XX
        23-06-19 부터 월-수 10건
        23-08-02 부터 월-수 12건
        2023-11월 1달간 리퍼중지
        2024-01-02부터 월-수 15건
        2024-02-26 월-금 10건
        2024-04-25 월-금 일7건"

        "선혜영 화-금 10건 (추가X) 
        칠곡O 
        경북대, 인하대, 중앙대, 계명대, 대전성모 XX esophagus CT XX 
        고대안산은 5건만! 
        2024-03-07부터 화-금 10건
        2024-03-07부터 고려대병원입사_고대안산리퍼X"

    - 필요한 정보들
        1. 판독의 계약유효 여부   -> Profile in_contract='Yes'/'No'/'Suspended'
        2. 판독의 기본 요일별 근무시간  -> 완료
           판독의 휴무일 등록 -> 완료
        3. 판독의 요일별 모달리티별 희망 리퍼수 -> 별도 테이블 필요 / dr, modality, target, maximum 
        4. 판독의 기피 병원, 기피 병원 모달러티 -> 별도 테이블 필요 / dr, customer, created_at
        5. 판독의별 리퍼 세팅 정보 변경 이력  -> 별도 로그테이블 필요 / created_at, dr, agent, description

    - Availability 함수
        1. 인자: dr, date, customer, modality, 
        2. return : 가능, 불가능

    - AvaliableQty 함수
        1. 인자: dr, date/time, modality 
        2. return: int() 개

# 11/11/2024 #
    - Referify
        1. 실시간으로 Radio의 처리 완료에 따라서 Case를 배정해주는 로직 필요
        







    
