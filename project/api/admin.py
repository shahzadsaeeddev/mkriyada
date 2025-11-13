from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(EgsLocations)
admin.site.register(SupplierDetails)
admin.site.register(Production)
admin.site.register(Company)


@admin.register(CustomerDetail)
class CustomerDetailAdmin(admin.ModelAdmin):
    search_fields = ['name_en', 'name_ar']
    list_filter = ['company__name']
    list_display = ['serial_no', 'name_en', 'name_ar', 'email', ]



@admin.register(Invoice)
class InvoicesDetailAdmin(admin.ModelAdmin):
    search_fields = ['serial_no', 'transaction_type']
    list_filter = ['company__name']
    list_display = ['serial_no', 'customer', 'date', 'transaction_type', 'transaction_status']

admin.site.register(SubscriptionPlan)

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    search_fields = ['orderID', 'payerID']
    list_filter = ['company__name']
    list_display = ['orderID', 'payerID', 'amount', 'status']

# admin.site.register(Sandbox)

@admin.register(Sandbox)
class SandboxAdmin(admin.ModelAdmin):
    list_filter = ['company__name']


@admin.register(ProductInvoice)
class ProductInvoiceAdmin(admin.ModelAdmin):
    search_fields = ['serial_no']
    list_filter = ['company__name']
    list_display = ['invoice__serial_no', 'item__name', 'invoice__transaction_type', 'total']

admin.site.register(CurrencyCodes)
admin.site.register(TaxType)
admin.site.register(PaymentTerms)
admin.site.register(Country)
