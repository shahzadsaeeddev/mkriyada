from .imports import *
from product.activityLogsMixins import ActivityLogMixin

from accounts.permissions import HasCustomerRole


class CustomerListCreateApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | HasCustomerRole]
    serializer_class = CustomerSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['street_name', 'building_number', 'city_subdivision_name', 'city_name', 'postal_zone',
                     'registered_name', 'vat_number']
    queryset = CustomerDetail.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance


class CustomerDetailApiView(CompanyQuerysetMixin, generics.ListAPIView):
    permission_classes = [HasAPIKey | HasCustomerRole]
    serializer_class = CustomerDetailsSerializer


    def get_queryset(self):
        company = self.get_company()
        return CustomerDetail.objects.filter(company=company)


class CustomerRetrieveUpdateDeleteApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [HasAPIKey | HasCustomerRole]
    serializer_class = CustomerSerializer
    queryset = CustomerDetail.objects.all()
    lookup_field = 'pk'



