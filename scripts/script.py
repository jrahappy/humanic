# from customer.models import (
#     Company,
# )
# from accounts.models import CustomUser
# from collab.models import Refers, ReferHistory
# from collab.views import create_history
import datetime


# def run():

#     HumanIC = CustomUser.objects.get(username="HumanIC")

#     refers = Refers.objects.filter(
#         status__in=["Requested"],
#         referred_date__lt=datetime.datetime.now() - datetime.timedelta(days=60),
#     ).order_by("referred_date")

#     for refer in refers:
#         refer.status = "Archived"
#         refer.updated_at = datetime.datetime.now()
#         refer.save()

#         ReferHistory.objects.create(
#             refer=refer,
#             changed_status="Cancelled",
#             memo="Refer cancelled due to inactivity.",
#             changed_by=HumanIC,
#             changed_at=datetime.datetime.now(),
#         )

#     print(
#         f"Updated {refers.count()} refers to 'Archived' status and created history entries."
#     )
# companies = Company.objects.all()
# for com in companies:
#     cellphone = com.office_fax
#     com.office_cellphone = cellphone
#     com.office_fax = None
#     com.save()
#     print(
#         f"Updated company {com.business_name}: office_cellphone set to {cellphone}, office_fax cleared."
#     )

from minibooks.models import ReportMaster, UploadHistory, MagamMaster


def run():

    # 마감대상 rows를 업데이트하는 스크립트
    # mg = MagamMaster.objects.get(id=30)
    # ayear = mg.ayear
    # amonth = mg.amonth

    # total_target = ReportMaster.objects.filter(ayear=ayear, amonth=amonth).count()

    # mg.target_rows = total_target
    # mg.save()
    # print(f"Updated MagamMaster with ID {mg.id} to target_rows {total_target}")

    # UploadHistory의 row_count를 업데이트하는 스크립트
    # ayear = "2025"
    # amonth = "5"
    # platform = "ONPACS"

    # # Create a new ReportMaster instance
    # a_raw = UploadHistory.objects.filter(
    #     # ayear=ayear, amonth=amonth, platform=platform
    #     id=142
    # ).first()

    # total = ReportMaster.objects.filter(uploadhistory=a_raw).count()

    # a_raw.row_count = total
    # a_raw.save()

    # print(f"Total ReportMaster count for {ayear}-{amonth} on {platform}: {total}")

    # UploadHistory의 row_count를 업데이트하는 스크립트
    ayear = "2025"
    amonth = "5"

    # Create a new ReportMaster instance
    a_raw = UploadHistory.objects.filter(
        # ayear=ayear, amonth=amonth, platform=platform
        id=145
    ).first()

    rms = ReportMaster.objects.filter(uploadhistory=a_raw)

    i = 0
    for rm in rms:
        if not rm.requestdttm or not rm.approveddttm:
            print(f"Skipping ReportMaster ID {rm.id} due to missing dates.")
            continue

        try:
            rqdt = datetime.datetime.strptime(rm.requestdttm, "%Y-%m-%d %H:%M:%S")
            apdt = datetime.datetime.strptime(rm.approveddttm, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Date parsing error for ReportMaster ID {rm.id}: {e}")
            continue

        rm.requestdt = rqdt
        rm.approvedt = apdt
        rm.save()
        i += 1

    print(f"Total Updated count for {ayear}-{amonth} : {i}")
