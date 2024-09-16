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
    