import django_filters
from accounts.models import Profile, CustomUser


class ProfileFilter(django_filters.FilterSet):

    class Meta:
        model = Profile
        fields = [
            "specialty2",
            "contract_status",
        ]
