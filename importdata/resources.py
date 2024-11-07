from import_export import resources
from .models import rawdata, temp_doctor_table, temp_customer_table


class rawdataResource(resources.ModelResource):
    class Meta:
        model = rawdata
        fields = (
            # "id",
            "apptitle",
            "case_id",
            "name",
            "department",
            "bodypart",
            "modality",
            "equipment",
            "studydescription",
            "imagecount",
            "accessionnumber",
            "readprice",
            "reader",
            "approver",
            "radiologist",
            "studydate",
            "approveddttm",
            "stat",
            "pacs",
            "requestdttm",
            "ecode",
            "sid",
            "patientid",
            "created_at",
            "cleaned",
            "verified",
            "importhistory",
            "updated_at",
        )


class doctorResource(resources.ModelResource):
    class Meta:
        model = temp_doctor_table
        fields = "__all__"


class customerResource(resources.ModelResource):
    class Meta:
        model = temp_customer_table
        fields = "__all__"
