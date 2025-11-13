from rest_framework import serializers
from ..models import CurrencyCodes, PaymentTerms, TaxType


class CurrencyCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyCodes
        fields = ['id', 'code', 'name']


class PaymentTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTerms
        fields = ['id', 'code', 'due_days']


class TaxTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxType
        exclude = ['company']
