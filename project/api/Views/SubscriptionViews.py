from rest_framework.filters import SearchFilter
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, get_object_or_404

from .imports import *
from accounts.permissions import HasPlanRole

from accounts.permissions import HasPaymentRole


class CompanyPlanRetrieveView(generics.RetrieveAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = CompanyPlanSerializer

    def get_object(self):
        api_key = self.request.headers.get('Authorization')
        company = None

        if api_key and api_key.startswith('Api-Key '):
            key = api_key.split(' ')[1]
            try:
                company = Company.objects.get(api_key=key)
            except Company.DoesNotExist:
                raise PermissionDenied("Invalid API key, company not found.")
        elif self.request.user and self.request.user.is_authenticated:
            company = self.request.user.company
        else:
            raise PermissionDenied("Authentication required: Provide an API key or be authenticated.")

        return company


class SubscriptionPlanListView(generics.ListAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = SubscriptionPlanListSerializer
    queryset = SubscriptionPlan.objects.filter(default = False)

    def get_object(self):
        api_key = self.request.headers.get('Authorization')
        company = None

        if api_key and api_key.startswith('Api-Key '):
            key = api_key.split(' ')[1]
            try:
                company = Company.objects.get(api_key=key)
            except Company.DoesNotExist:
                raise PermissionDenied("Invalid API key, company not found.")
        elif self.request.user and self.request.user.is_authenticated:
            company = self.request.user.company
        else:
            raise PermissionDenied("Authentication required: Provide an API key or be authenticated.")

        return company




class PaymentHistoryListView(generics.ListAPIView):
    permission_classes = [HasAPIKey | HasPaymentRole]
    serializer_class = PaymentHistorySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    pagination_class = StandardResultsSetPagination
    filterset_class = PaymentHistoryFilter
    search_fields = ['orderID']
    queryset = PaymentHistory.objects.all()

    def get_queryset(self):
        api_key = self.request.headers.get("Authorization")
        if api_key and api_key.startswith("Api-Key "):
            key = api_key.split(" ")[1]
            try:
                company = Company.objects.get(api_key=key)
                return PaymentHistory.objects.filter(company=company)
            except Company.DoesNotExist:
                return PaymentHistory.objects.none()
        else:
            user = self.request.user
            if user and user.is_authenticated:
                return PaymentHistory.objects.filter(company=user.company)



class SubscriptionPlanListCreateView(ListCreateAPIView):
    permission_classes = [HasPlanRole]
    serializer_class = SubscriptionPlanListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'invoice_limit']

    def get_queryset(self):
        return SubscriptionPlan.objects.all()


class SubscriptionPlanRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = [HasPlanRole]
    serializer_class = SubscriptionPlanListSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        pk = self.kwargs.get(self.lookup_field)
        return SubscriptionPlan.objects.filter(id=pk)



class SubscriptionControlApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company', None)
        action = request.data.get('action', None)
        plan_id = request.data.get('plan', None)
        invoice_limit = request.data.get('invoice_limit', None)
        user_limit = request.data.get('user_limit', None)

        if not company_id or not plan_id:
            return Response(
                {"error": "Company ID and Plan ID are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        company = get_object_or_404(Company, id=company_id)
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        company.plan = plan
        if invoice_limit is not None:
            company.max_invoices = invoice_limit
        if user_limit is not None:
            company.max_users = user_limit
        if action is not None:
            company.action = action
        company.save()

        return Response({"status": "Plan updated successfully"}, status=status.HTTP_200_OK)


