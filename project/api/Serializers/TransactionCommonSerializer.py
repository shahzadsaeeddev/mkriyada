from rest_framework import serializers
from .SerializerMixins import QrCodeMixin, AmountInWordsMixins
from ..models import ProductInvoice, Invoice, CustomerDetail, Company


class ProductInvoiceLineSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_uom = serializers.CharField(source='item.umo.name', read_only=True)

    class Meta:
        model = ProductInvoice
        exclude = ['updated_at', 'company', 'invoice', 'total_inclusive_tax_amount', 'cost']


class GeneralViewSerializer(QrCodeMixin, serializers.ModelSerializer):
    transaction = ProductInvoiceLineSerializer(many=True)
    customer_name = serializers.CharField(source='customer.name_en', read_only=True)
    company_name = serializers.CharField(source='company.name_ar', read_only=True)
    address = serializers.CharField(source='company.district', read_only=True)

    class Meta:
        model = Invoice
        exclude = ['updated_at', 'company', 'currency', 'payment_terms', 'uuid', 'hash', 'icv',
                   'invoice_lines', 'xml_string', 'status_response', 'transaction_type',
                   'document_types']


class SalePrintCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = ['id', 'name_en', 'name_ar', 'contact_no', 'vat_no', 'address', 'address_ar', 'license_no']


class SalePrintCompanyDetailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='media_file.file', read_only=True)
    postal_code = serializers.CharField(source='supplier.postal_zone', read_only=True)
    vat_number = serializers.CharField(source='supplier.vat_number', read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'name', 'name_ar', 'phone', 'email', 'address', 'district', 'bank_name', 'bank_address',
                  'account_number', 'iban_number', 'swift_code', 'district_ar', 'beneficiary_name', 'postal_code',
                  'vat_number', 'thumbnail']


class SalePrintGeneralViewSerializer(QrCodeMixin, AmountInWordsMixins,  serializers.ModelSerializer):
    transaction = ProductInvoiceLineSerializer(many=True)
    payment_terms = serializers.CharField(source='payment_terms.code', read_only=True)
    discount = serializers.CharField(source='transaction.discount', read_only=True)
    total_en = serializers.SerializerMethodField()
    total_ar = serializers.SerializerMethodField()
    customer_data = SalePrintCustomerSerializer(source="customer", read_only=True)
    company_data = SalePrintCompanyDetailSerializer(source="company", read_only=True)

    class Meta:
        model = Invoice
        exclude = ['updated_at', 'currency', 'uuid', 'hash', 'icv',
                   'invoice_lines', 'xml_string', 'status_response', 'transaction_type',
                   'document_types', 'company', 'customer']





class ReturnInvoiceNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'serial_no']
