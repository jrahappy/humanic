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

    "전우선"
    "송용섭"
    "이주원"
    "김예나"
    "이은정"
    "정미선"
    "전주현"
    "김리현"
    "유은혜"
    "손규리"
    "우현식"
    "이웅재"
    "김혜진"
    "김희정"

## 화상회의 09/25/2024 ##

  손경선 kasia71@humic.co.kr
  이종엽 yuphim@humic.co.kr

    ** 개선해야할 부분
    1. 휴먼외래와 전체 판독료를 분리해서 합산해서 보여주야 함.
    2. 동명 2인... 김혜진 145
    3. 동명이인의 경우에 정확성을 기하기 위해 Approver 로 구분함.
    4. 판독의 검색이 쉽게 함.

    문제점 : 
     CR, CT 가격이 너무 낮은 경우는 휴먼외래에도 적용되는지? 
     CTROW 이슈 Chest CT(비조영) 판독단가 19,600원 이하 건 → 14,700원 조정.. 어떻게 아는지.. 

        "CHEST TO PELVIS"
        "CHEST/SPINE"
        "CHEST\PELVIS"
        "CHEST PA"
        "CHEST\NECK"
        "CHEST/NECK"
        "CHEST LUNG"
        "Chest Lung"
        "CHEST LAT"
        "CHEST/HEAD"
        "CHEST [DIRECT]"
        "CHEST\CT_CHEST(ENHANCEMENT)"
        "CHEST/CSPINE"
        "CHEST AP"
        "CHESTABDPELVIS"
        "CHEST\ABDOMEN"
        "CHEST/ABDOMEN"
        "CHEST,ABDOMEN"
        "CHEST"
        "Chest"
        "chest"
        "ABODOMEN SUPINE"
        "abodomen"
        "ABDOMEN  SUPINE"
        "ABDOMEN SUPINE"
        "ABDOMENPELVIS"
        "Abdomen+Pelvis"
        "Abdomen + Pelvis"
        "Abdomen+pelvis"
        "ABDOMEN\PANCREAS"
        "ABDOMEN/NECK"
        "ABDOMEN\LIVER"
        "ABDOMEN/HEAD"
        "ABDOMEN/EXTREMITY"
        "ABDOMEN ERECT"
        "ABDOMEN\CHEST"
        "ABDOMEN/CHEST"
        "ABDOMEN\BILEDUCT\PANCREAS\LIVER"
        "ABDOMEN"
        "Abdomen"

## 09/27/2024 ##
    
    - Rule: 휴먼외래 건들에 대한 US, XA, FR 건 판독료 지급 제외 Rule 완료 
    - Rule: 대표원장단(김성현, 이재희) 판독료 계산 처리 완료
    - 개별 의사별 판독표 재계산 함수 완료
    
    => 모든 의사별 판독료 계산 완료
    
## 09/29/2024 ##
    - bodypart 의 정규화 방안 검토
    - 병원은 사업자번호, 판독의는 면허번호 추가 검토