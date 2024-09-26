    SELECT 
    "accounts_profile"."real_name", 
    "reportmaster"."provider_id", 
    SUM("reportmaster"."readprice") AS "total_price", 
    SUM("reportmaster"."pay_to_provider") AS "total_provider", 
    SUM("reportmaster"."pay_to_human") AS "total_human", 
    COUNT("reportmaster"."case_id") AS "total_cases", 
    (SELECT SUM(U0."pay_to_provider") AS "human_total_provider" 
    FROM "reportmaster" U0 
    WHERE (U0."amonth" = 7 AND U0."ayear" = 2024 AND U0."company_id" = 1 AND U0."provider_id" = ("reportmaster"."provider_id")) 
    GROUP BY U0."provider_id" 
    LIMIT 1) AS "huma_total_provider" 
    FROM "reportmaster" 
    LEFT OUTER JOIN "accounts_customuser" 
    ON ("reportmaster"."provider_id" = "accounts_customuser"."id") 
    LEFT OUTER JOIN "accounts_profile" 
    ON ("accounts_customuser"."id" = "accounts_profile"."user_id") 
    WHERE ("reportmaster"."amonth" = 7 AND "reportmaster"."ayear" = 2024) 
    GROUP BY "accounts_profile"."real_name", "reportmaster"."provider_id", 7 
    ORDER BY "accounts_profile"."real_name" ASC