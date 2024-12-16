from import_export import resources
from .models import IllnessCode


class IllnessCodeResource(resources.ModelResource):
    class Meta:
        model = IllnessCode
        fields = ("code", "name", "eng_name")
        import_id_fields = ("code", "name", "eng_name")
