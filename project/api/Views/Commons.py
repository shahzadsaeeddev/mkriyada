from .imports import *
from product.models import ProductItems

from ..Serializers.Commons import CountrySerializer
from ..Serializers.TransactionCommonSerializer import SalePrintGeneralViewSerializer
from ..models import Country


class DashboardApiView(APIView):
    permission_classes = [HasAPIKey | IsAuthenticated]

    def get_queryset(self):
        api_key = self.request.headers.get("Authorization")
        if api_key and api_key.startswith("Api-Key "):
            key = api_key.split(" ")[1]
            try:
                company = Company.objects.get(api_key=key)
                return Invoice.objects.filter(company=company)
            except Company.DoesNotExist:
                return Invoice.objects.none()
        return Invoice.objects.filter(company=self.request.user.company)

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        document_types = request.query_params.get('document_types')

        queryset = self.get_queryset()

        if start_date and end_date:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
            queryset = queryset.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
            )

        if document_types:
            document_types = document_types.split(",")
            queryset = queryset.filter(document_types__in=document_types)

        total_invoices = queryset.count()

        invoice_status_counts = queryset.values('status_code').annotate(count=models.Count('id'))
        status_counts = {entry['status_code']: entry['count'] for entry in invoice_status_counts}

        invoice_document_types = queryset.values('document_types').annotate(count=models.Count('id'))
        document_types_counts = {entry['document_types']: entry['count'] for entry in invoice_document_types}

        possible_statuses = ["REPORTED", "CLEARED", "NOT_REPORTED", "NOT_CLEARED"]
        possible_document_types = ["Standard_invoice", "Simplified_invoice", "Standard_credit_note",
                                   "Simplified_credit_note", "Standard_debit_note", "Simplified_debit_note"]

        for status in possible_statuses:
            status_counts.setdefault(status, 0)

        for doc_type in possible_document_types:
            document_types_counts.setdefault(doc_type, 0)

        return Response({
            "total_invoices": total_invoices,
            "invoice_status": status_counts,
            "document_types": document_types_counts,
        })


def Index(requests):
    return HttpResponse("Oops, Invalid URL Parameter")


class LocationView(viewsets.ModelViewSet):
    queryset = EgsLocations.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['registered_address', 'organisation', 'organisation_unit']

    def perform_create(self, serializer):
        return serializer.save(company=self.request.user.company, seller_name=self.request.user.username,
                               tax_no=self.request.user,
                               common_name=self.request.user.username)

    def get_queryset(self):
        return EgsLocations.objects.filter(company=self.request.user.company)



class LocationListView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    def get_queryset(self):
        return EgsLocations.objects.filter(company=self.request.user.company)


class BusinessLocationView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessLocationSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return EgsLocations.objects.filter(company=self.request.user.company)


class GenerateCSID(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, location, *args, **kwargs):
        results = CSIDSeliazer().data
        return Response(results)

    def patch(self, request, location, *args, **kwargs):
        c = self.request.user.company.filter(authentication_token=location).first()

        if c == None:
            return Response(
                {"status": "400", "Message": "Failed", "data": "account not found with current secret key"},
                status=400)
        if 'production' == request.data['scope']:
            slz = ProductionSerializer(c.production, data=request.data)
        if slz.is_valid():

            return Response(
                {"status": "200", "Message": "Success", "data": slz.data},
                status=200)
        else:
            return Response(
                {"status": "200", "Message": "Success", "data": slz.errors},
                status=400)


class ProductionView(generics.RetrieveUpdateAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'company'

    def get_object(self, queryset=None):
        company = self.kwargs.get('company')
        obj = Production.objects.get(company=company)
        return obj


class ProductionX509View(generics.RetrieveUpdateAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionX509Serializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'company'

    def get_object(self, queryset=None):
        company = self.kwargs.get('company')
        obj = Production.objects.get(company=company)
        return obj


class CustomerNoGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefix = request.query_params.get('type')
        location = request.user.company

        if not prefix:
            return Response({"detail": "Account prefix (`type`) is required in URL, e.g., ?type=SA"},
                            status=status.HTTP_400_BAD_REQUEST)

        prefix = prefix.upper()

        if prefix == 'CU':
            model = CustomerDetail
        elif prefix == 'PRD':
            model = ProductItems
        elif prefix in ['SI', 'CN', 'DN']:
            model = Invoice
        else:
            return Response({"detail": f"Unsupported prefix: {prefix}"}, status=status.HTTP_400_BAD_REQUEST)

        count = model.objects.filter(company=location, serial_no__startswith=f"{prefix}-").count() + 1

        generated_code = f"{prefix}-{count:05d}"

        return Response({"code": generated_code}, status=status.HTTP_200_OK)


class InvoiceSerialGenerateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefix = request.query_params.get('type')
        location = request.user.company

        if not prefix:
            return Response({"detail": "Account prefix (`type`) is required in URL, e.g., ?type=SA"},
                            status=status.HTTP_400_BAD_REQUEST)

        prefix = prefix.upper()

        count = Invoice.objects.filter(company=location, invoice_number__startswith=f"{prefix}-").count() + 1

        generated_code = f"{prefix}-{count:05d}"

        return Response({"code": generated_code}, status=status.HTTP_200_OK)



class TransactionsGeneralView(CompanyQuerysetMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = GeneralViewSerializer
    queryset = Invoice.objects.all()
    lookup_field = 'pk'


class SalePrintGeneralView(CompanyQuerysetMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = SalePrintGeneralViewSerializer
    queryset = Invoice.objects.all()
    lookup_field = 'pk'




class ReturnInvoiceApiView(CompanyQuerysetMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = ReturnInvoiceNumberSerializer

    def get_queryset(self):
        return Invoice.objects.filter(company=self.get_company(), transaction_type="sale")



class CountryListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = CountrySerializer
    queryset = Country.objects.all()