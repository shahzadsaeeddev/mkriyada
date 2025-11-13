from django.contrib.admin.utils import lookup_field

from .imports import *
from ..Serializers.InitTransactionsSerializer import CurrencyCodesSerializer, PaymentTermsSerializer, TaxTypeSerializer
from ..models import CurrencyCodes, PaymentTerms, TaxType


class InitTransactionApiView(CompanyQuerysetMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        company = self.get_company()
        customer_qs = company.customerdetail_data.all().order_by('-created_at')
        currency_qs = company.currencycodes_data.all().order_by('-created_at')
        payment_term_qs = PaymentTerms.objects.all().order_by('-created_at')


        data = {
            "customer": CustomerDetailsSerializer(customer_qs, many=True).data,
            "currency": CurrencyCodesSerializer(currency_qs, many=True).data,
            "payment_terms": PaymentTermsSerializer(payment_term_qs, many=True).data,
        }

        return Response(data)



class CurrencyCodeListCreateApiView(CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CurrencyCodesSerializer

    def get_queryset(self):
        return CurrencyCodes.objects.filter(company=self.get_company())

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())



class PaymentTermsListCreateApiView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentTermsSerializer
    queryset = PaymentTerms.objects.all()


class TaxTypeListCreateApiView(CompanyQuerysetMixin, generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaxTypeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return TaxType.objects.filter(company=self.get_company())

    def perform_create(self, serializer):
        serializer.save(company=self.get_company())


class TaxTypeRetrieveUpdateApiView(CompanyQuerysetMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TaxTypeSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return TaxType.objects.filter(company=self.get_company())



