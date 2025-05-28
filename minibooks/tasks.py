from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.utils import timezone
from datetime import date
from calendar import monthrange
from tablib import Dataset
from .models import UploadHistory, Company, ReportMaster
import logging

logger = logging.getLogger(__name__)


@shared_task
def upload_file(file_name, file_content):
    path = default_storage.save(file_name, ContentFile(file_content))
    return path


@shared_task(bind=True)
def update_is_onsite(self, row_id, is_onsite):
    is_onsite = True if is_onsite == "True" else False
    rm = ReportMaster.objects.get(id=row_id)
    rm.is_onsite = is_onsite
    rm.save()
    # print(f"Updated is_onsite for row_id: {row_id} to {is_onsite}")

    return "Done"


@shared_task(bind=True, soft_time_limit=25 * 60, time_limit=30 * 60, max_retries=3)
def create_reportmaster_task(self, uploadhistory_id, user_id):
    """
    Celery task to process Excel file and create ReportMaster records.
    Args:
        uploadhistory_id: ID of the UploadHistory record.
        user_id: ID of the user who initiated the task.
    """
    a_raw = None
    try:
        # Fetch UploadHistory
        a_raw = UploadHistory.objects.get(id=uploadhistory_id)
        platform = a_raw.platform
        ayear = int(a_raw.ayear)
        amonth = int(a_raw.amonth)
        last_date = date(ayear, amonth, monthrange(ayear, amonth)[1])
        a_file = a_raw.afile

        # Constants
        humanic = Company.objects.get(id=1)

        # Load Excel file
        dataset = Dataset()
        new_rawdata = a_file
        imported_data = dataset.load(new_rawdata.read(), format="xlsx")
        total_rows = len(imported_data)
        logger.info(f"Total rows: {total_rows}/File: {a_file}/Platform: {platform}")

        # Track progress
        check_pre_work_count = ReportMaster.objects.filter(
            uploadhistory_id=uploadhistory_id
        ).count()
        starting_row = check_pre_work_count
        i = starting_row + 1
        total_processed = 0

        for data in imported_data:
            if data[0] is None:
                logger.info(f"Skip empty row {i}")
                i += 1
                continue

            try:
                # Update progress
                total_processed += 1
                # self.update_state(
                #     state="PROGRESS",
                #     meta={"current": total_processed, "total": total_rows},
                # )
                # logger.info(f"Processing row {i}")

                if platform == "ONPACS":
                    # Calculate imagecount before creating the object
                    try:
                        imagecount = int(data[10]) if data[10] else 0
                    except Exception:
                        imagecount = 0

                    ReportMaster.objects.create(
                        apptitle=str(data[0]).strip() if data[0] else "",
                        ein=str(data[1]).strip() if data[1] else "",
                        case_id=str(data[2]).strip() if data[2] else "",
                        name=str(data[3]).strip() if data[3] else "",
                        department=str(data[4]).strip() if data[4] else "",
                        bodypart=str(data[5]).strip() if data[5] else "",
                        specialty2=str(data[6]).strip() if data[6] else "",
                        modality=str(data[7]).strip() if data[7] else "",
                        equipment=str(data[8]).strip() if data[8] else "",
                        studydescription=str(data[9]).strip() if data[9] else "",
                        imagecount=imagecount,
                        accessionnumber=str(data[11]).strip() if data[11] else "",
                        readprice=data[12] or 0,
                        reader=str(data[13]).strip() if data[13] else "",
                        approver=str(data[14]).strip() if data[14] else "",
                        radiologist=(
                            str(data[15]).strip().replace("\n", "").replace("\t", "")
                            if data[15]
                            else ""
                        ),
                        radiologist_license=str(data[16]).strip() if data[16] else "",
                        studydate=str(data[17]).strip() if data[17] else "",
                        approveddttm=str(data[18]).strip() if data[18] else "",
                        stat=str(data[19]).strip() if data[19] else "",
                        child=str(data[20]).strip() if data[20] else "",
                        pacs=str(data[21]).strip() if data[21] else "",
                        requestdttm=str(data[22]).strip() if data[22] else "",
                        ecode=str(data[23]).strip() if data[23] else "",
                        sid=str(data[24]).strip() if data[24] else "",
                        patientid=str(data[25]).strip() if data[25] else "",
                        human_paid_all=str(data[26]).strip() if data[26] else "",
                        ayear=str(ayear),
                        amonth=str(amonth),
                        adate=last_date,
                        is_take=False,
                        created_at=date.today(),
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )
                elif platform == "TAKE":
                    ReportMaster.objects.create(
                        apptitle=str(data[0]).strip() if data[0] else "",
                        ein=str(data[1]).strip() if data[1] else "",
                        case_id=str(data[2]).strip() if data[2] else "",
                        name=str(data[3]).strip() if data[3] else "",
                        department=str(data[4]).strip() if data[4] else "",
                        bodypart=str(data[5]).strip() if data[5] else "",
                        specialty2=str(data[6]).strip() if data[6] else "",
                        modality=str(data[7]).strip() if data[7] else "",
                        equipment=str(data[8]).strip() if data[8] else "",
                        studydescription=str(data[9]).strip() if data[9] else "",
                        imagecount=data[10] or 0,
                        accessionnumber=str(data[11]).strip() if data[11] else "",
                        readprice=data[12] or 0,
                        reader=str(data[13]).strip() if data[13] else "",
                        approver=str(data[14]).strip() if data[14] else "",
                        radiologist=(
                            str(data[15]).strip().replace("\n", "").replace("\t", "")
                            if data[15]
                            else ""
                        ),
                        radiologist_license=str(data[16]).strip() if data[16] else "",
                        studydate=str(data[17]).strip() if data[17] else "",
                        approveddttm=str(data[18]).strip() if data[18] else "",
                        stat=str(data[19]).strip() if data[19] else "",
                        pacs=str(data[21]).strip() if data[21] else "",
                        requestdttm=str(data[22]).strip() if data[22] else "",
                        ecode=str(data[23]).strip() if data[23] else "",
                        sid=str(data[24]).strip() if data[24] else "",
                        patientid=str(data[25]).strip() if data[25] else "",
                        human_paid_all=str(data[26]).strip() if data[26] else "",
                        ayear=str(ayear),
                        amonth=str(amonth),
                        adate=last_date,
                        is_take=True,
                        created_at=date.today(),
                        uploadhistory=a_raw,
                        excelrownum=i,
                    )
                else:
                    # Human Medical Center Excel format
                    if ayear == 2023:
                        ReportMaster.objects.create(
                            apptitle="휴먼영상의학센터",
                            company=humanic,
                            case_id=str(data[6]).strip() if data[6] else "",
                            name=str(data[12]).strip() if data[12] else "",
                            bodypart=str(data[9]).strip() if data[9] else "",
                            equipment=str(data[7]).strip() if data[7] else "",
                            accessionnumber=str(data[10]).strip() if data[10] else "",
                            studydescription=str(data[9]).strip() if data[9] else "",
                            imagecount=data[15] or 0,
                            readprice=data[14] or 0,
                            approver=str(data[5]).strip() if data[5] else "",
                            radiologist=str(data[3]).strip() if data[3] else "",
                            radiologist_license=str(data[4]).strip() if data[4] else "",
                            studydate=str(data[1]).strip() if data[1] else "",
                            approveddttm=str(data[2]).strip() if data[2] else "",
                            pacs="HPACS",
                            requestdttm=str(data[1]).strip() if data[1] else "",
                            patientid=str(data[11]).strip() if data[11] else "",
                            ayear=str(ayear),
                            amonth=str(amonth),
                            adate=last_date,
                            is_human_outpatient=True,
                            is_take=False,
                            created_at=date.today(),
                            verified=False,
                            uploadhistory=a_raw,
                            excelrownum=i,
                        )
                    else:
                        ReportMaster.objects.create(
                            apptitle="휴먼영상의학센터",
                            company=humanic,
                            case_id=str(data[6]).strip() if data[6] else "",
                            name=str(data[12]).strip() if data[12] else "",
                            bodypart=str(data[9]).strip() if data[9] else "",
                            equipment=str(data[7]).strip() if data[7] else "",
                            accessionnumber=str(data[10]).strip() if data[10] else "",
                            studydescription=str(data[16]).strip() if data[16] else "",
                            imagecount=data[18] or 0,
                            readprice=data[17] or 0,
                            approver=str(data[5]).strip() if data[5] else "",
                            radiologist=str(data[3]).strip() if data[3] else "",
                            radiologist_license=str(data[4]).strip() if data[4] else "",
                            studydate=str(data[1]).strip() if data[1] else "",
                            approveddttm=str(data[2]).strip() if data[2] else "",
                            pacs="HPACS",
                            requestdttm=str(data[1]).strip() if data[1] else "",
                            patientid=str(data[11]).strip() if data[11] else "",
                            ayear=str(ayear),
                            amonth=str(amonth),
                            adate=last_date,
                            is_human_outpatient=True,
                            is_take=False,
                            created_at=date.today(),
                            verified=False,
                            uploadhistory=a_raw,
                            excelrownum=i,
                        )
                i += 1
            except Exception as e:
                logger.error(f"Error at row {i}: {e}")
                # Log to UploadHistory
                # a_raw.log_uploadhistory(
                #     user_id=user_id,
                #     action="Data Import",
                #     description=f"Failed: Error at row {i}: {e}",
                # )
                raise  # Retry the task

        # Mark as imported
        a_raw.imported = True
        a_raw.save()
        # a_raw.log_uploadhistory(
        #     user_id=user_id,
        #     action="Data Import",
        #     description=f"Success: {i} rows imported",
        # )
        logger.info(f"Task completed: {i} rows imported")

        return {"status": "Success", "rows_imported": i}
    except Exception as e:
        logger.error(f"Task failed: {e}")
        if a_raw is not None:
            # a_raw.log_uploadhistory(
            #     user_id=user_id, action="Data Import", description=f"Failed: {e}"
            # )
            raise self.retry(countdown=60, exc=e)  # Retry after 60 seconds
