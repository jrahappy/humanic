from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.utils import timezone
from datetime import date
from calendar import monthrange
from tablib import Dataset
from .models import UploadHistory, Company, ReportMaster
from accounts.models import Profile, CustomUser
from django.db.models import Q
import logging
import time


logger = logging.getLogger(__name__)


@shared_task(bind=True)
def long_running_task(self, seconds=20):
    """
    Example task that reports progress each second.
    """
    progress = ProgressRecorder(self)
    total = int(seconds)
    result = 0
    for i in range(total):
        time.sleep(1)  # simulate work
        result += i
        # update the bar (current, total[, description])
        progress.set_progress(i + 1, total, description=f"Step {i+1}/{total}")
    return {"sum": result, "message": "Done!"}


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
def clean_data_task(self, uploadhistory_id, user_id):
    try:
        v_uploadhistory = UploadHistory.objects.get(id=uploadhistory_id)
        v_rawdata = (
            ReportMaster.objects.filter(
                uploadhistory_id=uploadhistory_id, verified=False
            )
            .filter(Q(company=None) | Q(provider=None))
            .order_by("id")
        )

        progress = ProgressRecorder(self)
        v_rawdata_count = v_rawdata.count()
        # logger.info(f"Data cleaning started for {v_rawdata_count} rows for UploadHistory ID {uploadhistory_id}")

        ayear = v_uploadhistory.ayear
        amonth = v_uploadhistory.amonth

        def get_verified_object(model, field, value):
            obj = model.objects.filter(**{field: value}).first()
            return obj, obj is not None

        i = 0
        for data in v_rawdata:
            # logger.info(f"Processing ReportMaster ID {data.id}")
            company, company_verified = get_verified_object(
                Company, "business_name", data.apptitle
            )

            radiologist = data.radiologist
            radiologist = (
                radiologist.replace(" ", "").replace("\n", "").replace("\t", "")
            )
            if radiologist == "김수진(유방)":
                radiologist = "김수진"
            elif radiologist == "김수진(신경두경부)":
                radiologist = "김수진B"

            radiologist_profile, radiologist_verified = get_verified_object(
                Profile, "real_name", radiologist
            )
            radiologist = radiologist_profile.user if radiologist_verified else None

            equipment = data.equipment
            if equipment == "DR":
                amodality = "CR"
            elif equipment == "DT":
                amodality = "CR"
            else:
                amodality = equipment

            is_human_outpatient = data.apptitle == "휴먼영상의학센터"

            if data.requestdttm:
                try:
                    requestdt = timezone.make_aware(
                        timezone.datetime.strptime(
                            data.requestdttm, "%Y-%m-%d %H:%M:%S"
                        )
                    )
                    requestdt_verified = True
                except (ValueError, TypeError):
                    requestdt = None
                    requestdt_verified = data.pacs == "ONSITE"
            else:
                requestdt = None
                requestdt_verified = True

            if data.approveddttm:
                try:
                    approvedt = timezone.make_aware(
                        timezone.datetime.strptime(
                            data.approveddttm, "%Y-%m-%d %H:%M:%S"
                        )
                    )
                    approvedt_verified = True
                except (ValueError, TypeError):
                    approvedt = None
                    approvedt_verified = data.pacs == "ONSITE"
            else:
                approvedt = None
                approvedt_verified = True

            verified = all(
                [
                    company_verified,
                    radiologist_verified,
                    # requestdt_verified,
                    # approvedt_verified,
                ]
            )

            if verified and isinstance(data.id, int):
                ReportMaster.objects.filter(id=data.id).update(
                    company=company,
                    provider=radiologist,
                    amodality=amodality,
                    is_human_outpatient=is_human_outpatient,
                    # requestdt=requestdt,
                    # approvedt=approvedt,
                    verified=True,
                )
                # logger.info(f"Data for ReportMaster ID {data.id} / {i} verified")
                i += 1
                progress.set_progress(
                    i + 1, v_rawdata_count, description=f"In progress: {i+1}/{total}"
                )
            else:
                unverified_message = ""
                if not company_verified:
                    unverified_message += (
                        f"Company verification failed for ID {data.id}\n"
                    )
                if not radiologist_verified:
                    unverified_message += (
                        f"Radiologist verification failed for ID {data.id}\n"
                    )
                if not requestdt_verified:
                    unverified_message += (
                        f"Request date verification failed for ID {data.id}\n"
                    )
                if not approvedt_verified:
                    unverified_message += (
                        f"Approval date verification failed for ID {data.id}\n"
                    )

                ReportMaster.objects.filter(id=data.id).update(
                    verified=False,
                    unverified_message=unverified_message,
                )
                logger.warning(
                    f"Unverified data for ReportMaster ID {data.id}: {unverified_message}"
                )
                break

            # self.update_state(
            #     state="PROGRESS", meta={"current": i, "total": v_rawdata_count}
            # )

        v_rawdata = ReportMaster.objects.filter(
            uploadhistory_id=uploadhistory_id, verified=False
        )
        total_rows = v_rawdata.count()
        if total_rows == 0:
            v_uploadhistory.verified = True
            v_uploadhistory.save(update_fields=["verified"])
            # v_uploadhistory.log_uploadhistory(
            #     user_id=user_id,
            #     action="Data Cleaning",
            #     description="Data cleaned successfully.",
            # )
            # logger.info("Data cleaning completed successfully")
            return {"status": "Success", "rows_processed": i}
        else:
            # v_uploadhistory.log_uploadhistory(
            #     user_id=user_id,
            #     action="Data Cleaning",
            #     description=f"Failed: Data for ReportMaster ID {data.id} not verified.",
            # )
            # logger.error("Data cleaning failed due to unverified records")
            return {
                "status": "Failure",
                "rows_processed": i,
                "error": "Unverified records remain",
            }
    except Exception as e:
        logger.error(f"Task failed for UploadHistory ID {uploadhistory_id}: {e}")
        # v_uploadhistory.log_uploadhistory(
        #     user_id=user_id, action="Data Cleaning", description=f"Failed: {e}"
        # )
        raise self.retry(countdown=60, exc=e)


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

        progress = ProgressRecorder(self)
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

                # self.update_state(
                #     state="PROGRESS",
                #     meta={"current": total_processed, "total": total_rows},
                # )
                # logger.info(f"Processing row {i}")

                if platform == "ONPACS":
                    # Calculate imagecount before creating the object
                    imagecount = 0
                    # try:
                    #     if str(data[10]).strip() == "":
                    #         imagecount = 0
                    #     else:
                    #         imagecount = int(data[10])
                    # except Exception:
                    #     imagecount = 0

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
                    total_processed += 1
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
                    total_processed += 1

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
                    total_processed += 1
                i += 1
                progress.set_progress(i, total_rows, f"Processed row {i}/{total_rows}")

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
        a_raw.row_count = total_processed
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
