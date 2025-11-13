from rest_framework import serializers
from ..models import Invoice


class InvoiceReportingLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'serial_no', 'date', 'total_amount', 'transaction_type']


class SubscriptionInvoicesSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name_en')
    class Meta:
        model = Invoice
        fields = ['serial_no', 'date', 'customer_name', 'total_amount', 'transaction_status']