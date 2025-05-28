from rest_framework import viewsets
from customer.models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()[round(0) : round(100)]
    serializer_class = CompanySerializer
