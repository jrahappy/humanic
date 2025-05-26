from celery import shared_task
from .models import Refers
from collab.views import create_history
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
            create_history(request, refer.id, "Archived", "Archived")
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
