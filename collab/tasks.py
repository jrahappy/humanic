import csv
import os
from urllib.parse import quote
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from celery import shared_task
from customer.models import Company
from minibooks.models import ReportMaster
from accounts.models import CustomUser
from .models import Refers, ReferHistory
import datetime
import logging


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def update_refer_status(self):
    """
    Celery task to update the status of a R.
    It cycles the status through PENDING -> IN_PROGRESS -> COMPLETED -> FAILED -> PENDING.
    Includes basic logging and error handling.
    """
    HumanIC = CustomUser.objects.get(username="HumanIC")

    refers = Refers.objects.filter(
        status__in=["Requested"],
        referred_date__lt=datetime.datetime.now() - datetime.timedelta(days=60),
    ).order_by("referred_date")

    logger.info(f"Found {refers.count()} refers to update.")
    if not refers:
        logger.info("No refers found to update.")
        return
    updated_count = 0
    for refer in refers:
        try:
            current_status = refer.status
            # Determine the next status in the cycle

            next_status = "Cancelled"
            refer.status = next_status
            refer.updated_at = datetime.datetime.now()
            refer.save()
            ReferHistory.objects.create(
                refer=refer,
                changed_status="Cancelled",
                memo="Refer cancelled due to inactivity.",
                changed_by=HumanIC,
                changed_at=datetime.datetime.now(),
            )

            updated_count += 1
            logger.info(
                f"Refer '{refer.patient_name}' (ID: {refer.id}) "
                f"status updated from '{current_status}' to '{next_status}'. "
                f"Total updates: {refer.update_count}"
            )
        except Refers.DoesNotExist:
            logger.error(
                f"Refer with ID {refer.id} not found. "
                f"This task will not be retried as the record does not exist."
            )
            # Do not retry if the record simply doesn't exist, as it won't magically appear.
        except Exception as e:
            logger.error(f"Error updating Refer ID {refer.id}: {e}", exc_info=True)
            # Attempt to retry the task if an unexpected error occurs.
            try:
                raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
            except self.MaxRetriesExceededError:
                logger.critical(
                    f"Refer ID {refer.id}: Max retries exceeded for task update."
                )


@shared_task(bind=True, soft_time_limit=25 * 60, time_limit=30 * 60, max_retries=3)
def customer_month_csv(company_id, adate):
    try:
        # Fetch company and prepare file name
        company = Company.objects.get(id=company_id)

        business_name = company.business_name
        file_name = f"{adate}_{business_name}.csv"
        encoded_file_name = quote(file_name)

        # Define the path to save the CSV in media/csv_files
        csv_dir = os.path.join(settings.MEDIA_ROOT, "csv_files")
        os.makedirs(csv_dir, exist_ok=True)  # Create directory if it doesn't exist
        file_path = os.path.join(csv_dir, file_name)

        # Create the HttpResponse for download
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f"attachment; filename*=UTF-8''{encoded_file_name}"
        )
        response.write("\ufeff")  # BOM for Excel compatibility

        # Create CSV writer for the response
        writer = csv.writer(response)
        writer.writerow(
            [
                "Customer",
                "CaseID",
                "Patient",
                "Modality",
                "Emergency",
                "Price",
                "Requestd",
                "Radiologist",
                "Approved",
            ]
        )

        # Also write to a file in the media directory
        with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
            file_writer = csv.writer(csv_file)
            file_writer.writerow(
                [
                    "Customer",
                    "CaseID",
                    "Patient",
                    "Modality",
                    "Emergency",
                    "Price",
                    "Requestd",
                    "Radiologist",
                    "Approved",
                ]
            )

            # Fetch data (up to 2000 records)
            rpms = ReportMaster.objects.filter(company=company, adate=adate).order_by(
                "case_id"
            )

            # Write data to both response and file
            for rpm in rpms:
                row = [
                    rpm.company.business_name,
                    rpm.case_id,
                    rpm.name,
                    rpm.modality,
                    rpm.stat,
                    rpm.readprice,
                    rpm.requestdttm,
                    rpm.radiologist,
                    rpm.approveddttm,
                ]
                writer.writerow(row)
                file_writer.writerow(row)

        # Log the successful creation of the CSV file
        logger.info(f"CSV file created successfully: {file_path}")
        # Add a notice message for the user
        messages.success(
            None,
            f"CSV file for {company.business_name} on {adate} created successfully.",
        )
        return response

    except Exception as e:
        # Handle exceptions and retry if necessary
        return JsonResponse({"status": "Error", "message": str(e)}, status=500)
