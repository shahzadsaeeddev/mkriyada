from rest_framework.filters import SearchFilter

from .imports import *
from product.activityLogsMixins import ActivityLogMixin

from accounts.permissions import HasCreditNotesRole, HasDebitNoteRole, HasCredentialsRole, HasSaleRole

from accounts.keycloak import update_role_self


class InvoicesProductionListApiView(CompanyQuerysetMixin, generics.ListAPIView):
    permission_classes = [HasAPIKey | HasSaleRole]
    serializer_class = InvoiceProductionListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['serial_no', 'customer__name', 'customer__serial_no']
    queryset = Invoice.objects.filter(transaction_type="sale")


class InvoicesProductionApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.CreateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = InvoiceProductionCreateSerializer
    queryset = Invoice.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance


class InvoicesProductionCreditListApiView(CompanyQuerysetMixin, generics.ListAPIView):
    permission_classes = [HasAPIKey | HasCreditNotesRole]
    serializer_class = InvoiceProductionListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['serial_no', 'customer__name', 'customer__serial_no']
    queryset = Invoice.objects.filter(transaction_type="credit_note")



class InvoicesProductionCreditNoteApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | HasCreditNotesRole]
    serializer_class = InvoiceProductionCreditNoteSerializer
    queryset = Invoice.objects.filter(transaction_type="credit_note")

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance



class InvoicesProductionDebitListApiView(CompanyQuerysetMixin, generics.ListAPIView):
    permission_classes = [HasAPIKey | HasDebitNoteRole]
    serializer_class = InvoiceProductionListSerializer
    queryset = Invoice.objects.filter(transaction_type="debit_note")
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['serial_no', 'customer__name', 'customer__serial_no']



class InvoicesProductionDebitNoteApiView(ActivityLogMixin, CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = [HasAPIKey | HasDebitNoteRole]
    serializer_class = InvoiceProductionDebitNoteSerializer
    queryset = Invoice.objects.filter(transaction_type="debit_note")

    def perform_create(self, serializer):
        instance = serializer.save(company=self.get_company())
        self.log_activity("Create", instance)
        return instance


class ProductionValidateOtpApiView(APIView):
    permission_classes = [HasCredentialsRole]

    def post(self, request, *args, **kwargs):
        scope = request.data.get("scope")
        company = request.user.company

        if scope == "production":
            serializer = ProductionCredentialSerializer(instance=company, data=request.data)
            auth_header = request.META.get('HTTP_AUTHORIZATION', None)
            if not auth_header or not auth_header.startswith("Bearer "):
                raise serializers.ValidationError("Authorization token missing")
            auth_token = auth_header.split(" ")[1]
            company.enabled_zatca = True
            company.save()
            update_role_self(auth_token, request.user.username, company.name, company.enabled_zatca)
        else:
            return Response({"error": "Invalid scope"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            return Response({"message": "CSID and X509 generated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
