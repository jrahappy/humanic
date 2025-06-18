import os
import csv
import datetime
import logging
import re
from urllib.parse import quote
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from celery import shared_task
from customer.models import Company
from minibooks.models import ReportMaster
from accounts.models import CustomUser
from .models import Refers, ReferHistory
from django.utils import timezone
from django.db import DatabaseError


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
        referred_date__lt=timezone.now() - datetime.timedelta(days=60),
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
            refer.updated_at = timezone.now()
            refer.save()
            ReferHistory.objects.create(
                refer=refer,
                changed_status="Cancelled",
                memo="Refer cancelled due to inactivity.",
                changed_by=HumanIC,
                changed_at=timezone.now(),
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


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def update_cosigend_refer_status(self):
    """
    Celery task to update the status of a R.
    It cycles the status through PENDING -> IN_PROGRESS -> COMPLETED -> FAILED -> PENDING.
    Includes basic logging and error handling.
    """
    HumanIC = CustomUser.objects.get(username="HumanIC")

    refers = Refers.objects.filter(
        status__in=["Cosigned"],
        referred_date__lt=timezone.now() - datetime.timedelta(days=7),
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
            refer.updated_at = timezone.now()
            refer.save()
            ReferHistory.objects.create(
                refer=refer,
                changed_status="Archived",
                memo="Refer archived.",
                changed_by=HumanIC,
                changed_at=timezone.now(),
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
def customer_month_csv(self, company_id, adate):
    try:
        # Validate inputs
        try:
            company_id = int(company_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid company_id: {company_id}")
            return {"status": "error", "message": "Invalid company ID"}

        if not isinstance(adate, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", adate):
            logger.error(f"Invalid adate format: {adate}")
            return {"status": "error", "message": "Date must be YYYY-MM-DD"}

        # Fetch company
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            logger.error(f"Company with id {company_id} not found")
            raise self.retry(countdown=60)

        # Sanitize business_name
        business_name = "".join(
            c for c in company.business_name if c.isalnum() or c in (" ", "_")
        ).replace(" ", "_")
        file_name = f"{adate}_{business_name}.csv"
        encoded_file_name = quote(file_name)

        # Define CSV path
        csv_dir = os.path.join(settings.MEDIA_ROOT, "csv_files")
        os.makedirs(csv_dir, exist_ok=True)
        file_path = os.path.join(csv_dir, file_name)

        # Fetch data
        try:
            rpms = (
                ReportMaster.objects.filter(company=company, adate=adate)
                .select_related("company")
                .order_by("case_id")[:2000]
            )
        except DatabaseError as e:
            logger.error(f"Database error fetching ReportMaster: {e}")
            raise self.retry(countdown=60)

        # Create CSV content
        rows = [
            [
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
            for rpm in rpms
        ]

        # Write to file
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.writer(csv_file)
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
                writer.writerows(rows)
        except PermissionError as e:
            logger.error(f"Permission denied writing to {file_path}: {e}")
            raise self.retry(countdown=60)

        # Log success
        logger.info(f"CSV file created successfully: {file_path}")

        # Return result
        return {
            "status": "success",
            "file_path": file_path,
            "file_name": file_name,
            "company": business_name,
            "adate": adate,
        }

    except self.MaxRetriesExceededError:
        logger.error(
            f"Max retries exceeded for customer_month_csv: company_id={company_id}, adate={adate}"
        )
        return {"status": "error", "message": "Max retries exceeded"}
    except Exception as e:
        logger.exception(
            f"Error in customer_month_csv: company_id={company_id}, adate={adate}, error={str(e)}"
        )
        raise self.retry(countdown=60)
