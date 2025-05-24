from customer.models import (
    Company,
)


def run():

    companies = Company.objects.all()
    for com in companies:
        cellphone = com.office_fax
        com.office_cellphone = cellphone
        com.office_fax = None
        com.save()
        print(
            f"Updated company {com.business_name}: office_cellphone set to {cellphone}, office_fax cleared."
        )
