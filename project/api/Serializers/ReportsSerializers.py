from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from .ReportsMixins import SaleReportMixins, ProductReportMixins, CustomerReportMixins
from ..models import Invoice, CustomerDetail, ProductInvoice, Company
from product.models import ProductItems


class SaleReportSerializer(SaleReportMixins, serializers.ModelSerializer):
    item = serializers.SerializerMethodField(read_only=True)
    customer = serializers.CharField(source='customer.name', read_only=True)
    discount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Invoice
        exclude = ['company', 'updated_at', 'invoice_qrcode', 'status_response', 'status_code', 'xml_string',
                   'invoice_lines', 'icv', 'hash', 'uuid', 'currency', 'payment_terms']


class ZatcaSubmissionReportSerializer(SaleReportMixins, serializers.ModelSerializer):
    item = serializers.SerializerMethodField(read_only=True)
    customer = serializers.CharField(source='customer.name', read_only=True)
    discount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Invoice
        fields = ["serial_no", "date", "status_code", 'item', 'customer', "discount"]


class CustomerReportSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='customer.email', read_only=True)
    serial_no = serializers.CharField(source='customer.serial_no', read_only=True)
    name_en = serializers.CharField(source='customer.name_en', read_only=True)
    contact_no = serializers.CharField(source='customer.contact_no', read_only=True)
    vat_no = serializers.CharField(source='customer.vat_no', read_only=True)
    registered_name = serializers.CharField(source='customer.registered_name', read_only=True)
    status = serializers.CharField(source='customer.status', read_only=True)
    percentage_of_total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ['id', 'transaction_type', 'email', 'serial_no', 'name_en', 'contact_no', 'vat_no', 'registered_name',
                  'status']

    def get_percentage_of_total(self, obj):
        total_sales = self.context.get("total_sales") or 0
        sales_value = obj.get("sales_value") or 0
        if total_sales > 0:
            percent = (sales_value / total_sales) * 100
            return round(percent, 2)
        return 0.0


class ProductReportSerializer(ProductReportMixins, serializers.ModelSerializer):
    invoice_no = serializers.CharField(source='invoice.serial_no', read_only=True)
    date = serializers.CharField(source='invoice.date', read_only=True)
    due_date = serializers.CharField(source='invoice.due_date', read_only=True)
    transaction_typ = serializers.CharField(source='invoice.transaction_type', read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(source='item.name', read_only=True)
    unit_price = serializers.CharField(source='item.unit_price', read_only=True)
    serial_no = serializers.CharField(source='item.serial_no', read_only=True)
    item_type = serializers.CharField(source='item.item_type', read_only=True)
    tax_applied = serializers.BooleanField(source='item.tax_applied', read_only=True)


    class Meta:
        model = ProductInvoice
        exclude = ['company', 'updated_at']



class ItemSalesTrendSerializer(serializers.ModelSerializer):
    period = serializers.DateField()
    item_name = serializers.CharField(source="item__name")
    total_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = ProductInvoice
        fields = ["period", "item_name", "total_quantity", "total_sales"]


# -------------------- SALES GROWTH TREND --------------------
class SalesGrowthTrendSerializer(serializers.ModelSerializer):
    period = serializers.DateField()
    sales_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    growth_percent = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["period", "sales_value", "growth_percent"]

    def get_growth_percent(self, obj):
        return obj.get("growth_percent", Decimal(0))


# -------------------- CUSTOMER SALES TREND --------------------
class CustomerSalesTrendSerializer(serializers.ModelSerializer):
    period = serializers.DateField()
    invoice_count = serializers.IntegerField()
    customer_name = serializers.CharField(source="customer__name_en")
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Invoice
        fields = ["period", "customer_name", "total_sales", 'invoice_count']


# -------------------- TOP CUSTOMERS --------------------
class TopCustomersSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer__name_en")
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    invoice_count = serializers.IntegerField()
    percentage_of_total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["customer_name", "total_sales", 'invoice_count', 'percentage_of_total']

    def get_percentage_of_total(self, obj):
        total_sales_sum = self.context.get("total_sales_sum") or 0
        total_sales = obj.get("total_sales") or 0
        if total_sales_sum > 0:
            percent = (total_sales / total_sales_sum) * 100
            return round(percent, 2)
        return 0.0


# -------------------- SALES BY CATEGORY --------------------
class SalesByCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="item__category__name")
    total_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    sales_percent = serializers.SerializerMethodField()

    class Meta:
        model = ProductInvoice
        fields = ["category_name", "total_quantity", "total_sales", "sales_percent"]

    def get_sales_percent(self, obj):
        total_sales_sum = self.context.get("total_sales_sum", 0)
        total_sales = obj.get("total_sales", 0)
        if total_sales_sum > 0:
            return round(float(total_sales / total_sales_sum * 100), 2)
        return 0


# -------------------- TAX SALES --------------------
class TaxSalesReportSerializer(serializers.ModelSerializer):
    period = serializers.DateField()
    taxable_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    exempt_sales = serializers.DecimalField(max_digits=12, decimal_places=2)
    vat_value = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Invoice
        fields = ["period", "taxable_sales", "exempt_sales", "vat_value"]


class DocumentTypeReportSerializer(serializers.ModelSerializer):
    period = serializers.DateField()
    invoice_count = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = Invoice
        fields = ['period', 'document_types', 'invoice_count', 'total_value']




class SubscriptionPlanReportSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(source="plan.name", read_only=True)
    class Meta:
        model = Company
        fields = ['id', 'name', 'contact_name', 'email', 'plan', 'expiry', 'max_invoices']


class SystemReportSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ['id', 'name', 'users', 'documents']

    def get_users(self, obj):
        users = obj.users
        if users:
            return users.count()
        return 0

    def get_documents(self, obj):
        document = obj.invoice_data
        if document:
            return document.count()
        else:
            return 0