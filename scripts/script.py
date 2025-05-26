from customer.models import (
    Company,
)
from accounts.models import CustomUser
from collab.models import Refers, ReferHistory
from collab.views import create_history
import datetime


def run():

    HumanIC = CustomUser.objects.get(username="HumanIC")

    refers = Refers.objects.filter(
        status__in=["Requested"],
        referred_date__lt=datetime.datetime.now() - datetime.timedelta(days=60),
    ).order_by("referred_date")

    for refer in refers:
        refer.status = "Archived"
        refer.updated_at = datetime.datetime.now()
        refer.save()

        ReferHistory.objects.create(
            refer=refer,
            changed_status="Cancelled",
            memo="Refer cancelled due to inactivity.",
            changed_by=HumanIC,
            changed_at=datetime.datetime.now(),
        )

    # companies = Company.objects.all()
    # for com in companies:
    #     cellphone = com.office_fax
    #     com.office_cellphone = cellphone
    #     com.office_fax = None
    #     com.save()
    #     print(
    #         f"Updated company {com.business_name}: office_cellphone set to {cellphone}, office_fax cleared."
    #     )
