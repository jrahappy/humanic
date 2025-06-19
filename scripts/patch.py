from minibooks.models import ReportMaster, UploadHistory


def patch_report_master():

    ayear = "2025"
    amonth = "5"
    platform = "ONPACS"

    # Create a new ReportMaster instance
    a_raw = UploadHistory.objects.filter(
        ayear=ayear, amonth=amonth, platform=platform
    ).first()

    total = ReportMaster.objects.filter(UploadHistory=a_raw).count()

    print(f"Total ReportMaster count for {ayear}-{amonth} on {platform}: {total}")

    # if not a_raw:
    #     # If no UploadHistory found, return or handle accordingly
    #     print(f"No UploadHistory found for {ayear}-{amonth} on {platform}")
    #     return

    # else:
    #     print(f"Found UploadHistory for {ayear}-{amonth} on {platform}: {a_raw}")
    #     a_raw.row_count = total
    #     a_raw.save()
