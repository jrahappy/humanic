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

