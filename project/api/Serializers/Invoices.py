
from rest_framework import serializers
from ..models import Invoice


class InvoicesSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(write_only=True)
    invoice_lines = serializers.CharField(write_only=True)

    class Meta:
        model = Invoice
        exclude = ['updated_at', 'company']

