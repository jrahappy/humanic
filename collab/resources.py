from import_export import resources
from .models import IllnessCode, SimpleDiagnosis


class IllnessCodeResource(resources.ModelResource):
    class Meta:
        model = IllnessCode
        fields = ("code", "name", "eng_name")
        import_id_fields = ("code", "name", "eng_name")


class SimpleDiagnosisResource(resources.ModelResource):
    class Meta:
        model = SimpleDiagnosis
        fields = ("code1", "code2", "code3", "code4", "order")
        import_id_fields = ("code1", "code2", "code3", "code4", "order")
