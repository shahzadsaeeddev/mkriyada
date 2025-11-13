import json

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import CustomerDetail


class CustomerSerializer(serializers.ModelSerializer):
    currency_code = serializers.CharField(source="currency.code", read_only=True)
    class Meta:
        model = CustomerDetail
        exclude = ['updated_at', 'company', 'xml_text']



class CustomerDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = ['id', 'name_en']

