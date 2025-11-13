from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
from rest_framework_api_key.models import APIKey
from utility.modelMixins import TimeStampMixins, CompanyMixins, DefaultManager
from product.models import ProductItems
from utility.constants import InvoiceType, PaymentMethodsChoices, TransactionType, TransactionStatusChoices, \
    CompanyActionChoices, CompanyPhaseChoices, CompanyPortalChoices

from product.models import UnitOfMeasurements, Category, MediaFiles

User = get_user_model()


def generate_key():
    private_key = secrets.token_bytes(32)
    return private_key.hex()


class Country(TimeStampMixins):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=5, blank=True)
    currency = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class SubscriptionPlan(TimeStampMixins):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='subscription_plan', null=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    sale_price = models.DecimalField(max_digits=7, decimal_places=2)
    duration = models.PositiveIntegerField(null=True, blank=True)
    invoice_limit = models.PositiveIntegerField(null=True, blank=True)
    number_of_users = models.PositiveIntegerField(null=True, blank=True)
    api_access = models.BooleanField(default=False)
    support_level = models.CharField(max_length=255, blank=True)
    best_for = models.CharField(max_length=100, blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CurrencyCodes(CompanyMixins):
    name = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=5, null=True, blank=True)
    symbol = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class PaymentTerms(TimeStampMixins):
    code = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    due_days = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code)




class CompanyDetails(TimeStampMixins):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='company_address_details', null=True)
    country_iso = models.CharField(max_length=100, null=True, blank=True, verbose_name="Country ISO")
    district_ar = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company District in Arabic")
    city_ar = models.CharField(max_length=100, null=True, blank=True, verbose_name="City in Arabic")
    street_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Street Name")
    street_name_ar = models.CharField(max_length=100, null=True, blank=True, verbose_name="Street Name in Arabic")
    beneficiary_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Beneficiary Name")
    bank_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bank Name")
    bank_address = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bank Address")
    account_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Account Number")
    iban_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="IBAN Number")
    swift_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Swift Code")

    class Meta:
        abstract = True


class Company(CompanyDetails):
    media_file = models.ForeignKey(MediaFiles, on_delete=models.CASCADE, related_name='company_media_files', null=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True,
                             related_name="companies")
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company Name")
    name_ar = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company Name in Arabic")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Company Phone Number")
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Company Contact Name")
    email = models.CharField(max_length=100, blank=True, null=True, verbose_name="Company Contact Email")
    address = models.TextField(blank=True, null=True, verbose_name="Company Address")
    zatca_phase = models.CharField(max_length=100, blank=True, null=True, choices=CompanyPhaseChoices.choices,
                                   verbose_name="Company Zatca Phase")
    zatca_phase_start_date = models.DateTimeField(null=True, blank=True,
                                                  verbose_name="Company Zatca Phase 2 Start Date")
    portal = models.CharField(max_length=100, blank=True, null=True, choices=CompanyPortalChoices.choices,
                              verbose_name="Company Portal")
    tax_no = models.CharField(max_length=30, blank=True, null=True, verbose_name="Company Tax No")
    district = models.CharField(max_length=50, blank=True, null=True, verbose_name="Company District")
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name="Company City")
    expiry = models.DateField(null=True, blank=True, verbose_name="Company Expiry")
    enabled_zatca = models.BooleanField(default=False, verbose_name="Company Zatca Enabled")
    production_enable_zatca = models.BooleanField(default=False, verbose_name="Company Zatca Production Enabled")
    api_key = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company API Key")
    secret_key = models.CharField(max_length=100, null=True, blank=True, verbose_name="Company Secret Key")
    sandbox_secret_key = models.CharField(max_length=100, null=True, blank=True,
                                          verbose_name="Company Sandbox Secret Key")
    max_invoices = models.CharField(max_length=20, null=True, blank=True, verbose_name="Company Max Invoices")
    max_users = models.CharField(max_length=20, null=True, blank=True, verbose_name="Company Max Users")
    action = models.CharField(max_length=10, choices=CompanyActionChoices.choices, null=True, blank=True,
                              verbose_name="Company Action")

    def save(self, *args, **kwargs):
        if not self.api_key:
            slug_base = f"{self.name}"
            api_key, key = APIKey.objects.create_key(name=slug_base, expiry_date=self.expiry)
            self.api_key = key

        if not self.secret_key:
            self.secret_key = generate_key()

        if not self.sandbox_secret_key:
            self.sandbox_secret_key = generate_key()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TaxType(TimeStampMixins):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name="taxtype")
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Name")
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True, verbose_name="Tax Percentage")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    tax_category = models.CharField(blank=True, max_length=100, null=True, verbose_name="Tax Category")
    vat_group = models.CharField(blank=True, max_length=100, null=True, verbose_name="VAT Group")

    def __str__(self):
        return self.name



class EgsLocations(TimeStampMixins):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, blank=True, related_name="csr", null=True)
    tax_no = models.CharField(blank=True, max_length=16)
    common_name = models.CharField(null=True, blank=True, max_length=230)
    organisation = models.CharField(blank=True, max_length=230)
    organisation_unit = models.CharField(blank=True, max_length=230)
    serial_number = models.CharField(blank=True, max_length=230)
    choices = (('1000', 'B2B'), ('0100', 'B2C'), ('1100', 'Both'))
    title = models.CharField(blank=True, max_length=230, choices=choices)
    registered_address = models.CharField(blank=True, max_length=230)
    business_category = models.CharField(blank=True, max_length=230, null=True)
    objects = DefaultManager()

    def __str__(self):
        return f'{self.organisation}'


class SupplierDetails(TimeStampMixins):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, blank=True, related_name="supplier")
    # Invoice setup
    schemaList = (
        ('TIN', 'TIN'), ('GCC', 'GCC'), ('IQA', 'IQA'), ('PAS', 'PAS'), ('CRN', 'CRN'), ('MOM', 'MOM'), ('MLS', 'MLS'),
        ('700', '700'), ('SAG', 'SAG'), ('OTH', 'OTH'))
    scheme_type = models.CharField(max_length=50, verbose_name="Scheme ID", null=True, blank=True, choices=schemaList)
    scheme_no = models.BigIntegerField(verbose_name="Scheme Number", null=True, blank=True, )
    street_name = models.CharField(max_length=255, verbose_name="Street Name", blank=True, null=True)
    building_number = models.CharField(max_length=50, verbose_name="Building Number", blank=True, null=True)
    city_subdivision_name = models.CharField(max_length=255, verbose_name="City Subdivision Name", blank=True,
                                             null=True)
    city_name = models.CharField(max_length=255, verbose_name="City Name", blank=True, null=True)
    postal_zone = models.CharField(max_length=50, verbose_name="Postal Zone", blank=True, null=True)
    registered_name = models.CharField(max_length=50, verbose_name="Registered Name", blank=True, null=True)
    vat_number = models.CharField(max_length=50, verbose_name="vat number", blank=True, null=True)
    tax_scheme = models.CharField(max_length=50, verbose_name="Tax Type", blank=True, null=True)
    xml_text = models.TextField(verbose_name="XML Text", blank=True, null=True)
    objects = DefaultManager()

    def __str__(self):
        return f'{self.company.name}'


class Production(TimeStampMixins):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, blank=True, related_name="production")
    private_key = models.TextField(blank=True, max_length=1000)
    public_key = models.TextField(blank=True, max_length=1000)
    csr = models.TextField(blank=True, max_length=2500)
    csid = models.TextField(blank=True, max_length=3500, null=True)
    csid_base64 = models.TextField(blank=True, max_length=3500, null=True)
    secret_csid = models.TextField(blank=True, max_length=2500, null=True)
    csid_request = models.TextField(blank=True, max_length=100, null=True)
    x509_base64 = models.TextField(blank=True, max_length=3500, null=True)
    x509_certificate = models.TextField(blank=True, max_length=3500, null=True)
    x509_secret = models.TextField(blank=True, max_length=500, null=True)
    x509_request = models.TextField(blank=True, max_length=100, null=True)
    is_simplified_invoice = models.BooleanField(default=False, verbose_name="Is Simplified Invoice")
    is_simplified_debit_note = models.BooleanField(default=False, verbose_name="Is Simplified debit note")
    is_simplified_credit_note = models.BooleanField(default=False, verbose_name="Is Simplified credit note")
    is_standard_invoice = models.BooleanField(default=False, verbose_name="Is Standard Invoice")
    is_standard_debit_note = models.BooleanField(default=False, verbose_name="Is Standard debit note")
    is_standard_credit_note = models.BooleanField(default=False, verbose_name="Is Standard credit note")
    objects = DefaultManager()

    def __str__(self):
        return str(self.company.name)


class Sandbox(TimeStampMixins):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, blank=True, related_name="sandbox")
    private_key = models.TextField(blank=True, max_length=1000)
    public_key = models.TextField(blank=True, max_length=1000)
    csr = models.TextField(blank=True, max_length=2500)
    csid = models.TextField(blank=True, max_length=3500, null=True)
    csid_base64 = models.TextField(blank=True, max_length=3500, null=True)
    secret_csid = models.TextField(blank=True, max_length=2500, null=True)
    csid_request = models.TextField(blank=True, max_length=100, null=True)
    x509_base64 = models.TextField(blank=True, max_length=3500, null=True)
    x509_certificate = models.TextField(blank=True, max_length=3500, null=True)
    x509_secret = models.TextField(blank=True, max_length=500, null=True)
    x509_request = models.TextField(blank=True, max_length=100, null=True)
    is_simplified_invoice = models.BooleanField(default=False, verbose_name="Is Simplified Invoice")
    is_simplified_debit_note = models.BooleanField(default=False, verbose_name="Is Simplified debit note")
    is_simplified_credit_note = models.BooleanField(default=False, verbose_name="Is Simplified credit note")
    is_standard_invoice = models.BooleanField(default=False, verbose_name="Is Standard Invoice")
    is_standard_debit_note = models.BooleanField(default=False, verbose_name="Is Standard debit note")
    is_standard_credit_note = models.BooleanField(default=False, verbose_name="Is Standard credit note")
    objects = DefaultManager()

    def __str__(self):
        return f'{self.company.name}'


class CustomerDetail(CompanyMixins):
    TYPES_CHOICES = [
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
    ]
    LICENSE_CHOICES = [
        ('CRN', 'CRN'),
        ('VAT', 'VAT'),
        ('TIN', 'TIN'),
        ('GCC', 'GCC'),
        ('IQA', 'IQA'),
        ('PAS', 'PAS'),
        ('CRN', 'CRN'),
        ('MOM', 'MOM'),
        ('MLS', 'MLS'),
        ('700', '700'),
        ('SAG', 'SAG'),
        ('OTH', 'OTH')
    ]
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True,
                                related_name="customer_country", verbose_name="Country")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_details')
    serial_no = models.CharField(max_length=50, blank=True, verbose_name="Customer Number")
    name_en = models.CharField(max_length=150, blank=True, verbose_name="Customer Name")
    name_ar = models.CharField(max_length=150, blank=True, verbose_name="Customer Arabic Name")
    email = models.CharField(max_length=150, blank=True, verbose_name="Customer Email")
    contact_no = models.CharField(max_length=50, blank=True, verbose_name="Customer Contact Number")
    contact_name = models.CharField(max_length=150, blank=True, verbose_name="Customer Contact Name")
    status = models.BooleanField(default=False, verbose_name="Customer Status")
    type = models.CharField(max_length=50, choices=TYPES_CHOICES, blank=True, verbose_name="Customer Type")
    license_type = models.CharField(max_length=50, choices=LICENSE_CHOICES, blank=True, verbose_name="License Type")
    license_no = models.CharField(max_length=100, blank=True, verbose_name="Customer License Number")
    vat_no = models.CharField(max_length=100, blank=True, verbose_name="Customer VAT Registration Number")
    currency = models.ForeignKey(CurrencyCodes, on_delete=models.CASCADE, null=True, related_name="customer_currency")
    payment_method = models.CharField(max_length=100, choices=PaymentMethodsChoices.choices, blank=True,
                                      verbose_name="Payment Methods")
    payment_terms = models.ForeignKey(PaymentTerms, on_delete=models.CASCADE, null=True,
                                      related_name="customer_payment_terms")
    address = models.TextField(blank=True, verbose_name="Customer Address")
    address_ar = models.CharField(max_length=100, blank=True, verbose_name="Customer Address Arabic")

    country_code = models.CharField(max_length=5, blank=True, verbose_name="Customer Country Code")
    city = models.CharField(max_length=150, blank=True, verbose_name="Customer City")
    city_ar = models.CharField(max_length=150, blank=True, verbose_name="Customer City Arabic")
    postal_code = models.CharField(max_length=50, blank=True, verbose_name="Customer Postal Code")
    district = models.CharField(max_length=150, blank=True, verbose_name="Customer District")
    district_ar = models.CharField(max_length=150, blank=True, verbose_name="Customer District Arabic")
    street_name = models.CharField(max_length=255, verbose_name="Street Name", blank=True, null=True)
    street_name_ar = models.CharField(max_length=255, verbose_name="Street Name Arabic", blank=True, null=True)
    building_number = models.CharField(max_length=50, verbose_name="Building Number", blank=True, null=True)
    city_subdivision_name = models.CharField(max_length=255, verbose_name="City Subdivision Name", blank=True,
                                             null=True)
    registered_name = models.CharField(max_length=50, verbose_name="Registered Name", blank=True, null=True)
    bank_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bank Name")
    bank_address = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bank Address")
    account_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Account Number")
    iban_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="IBAN Number")
    swift_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Swift Code")
    xml_text = models.TextField(verbose_name="XML Text", blank=True, null=True)

    objects = DefaultManager()

    def __str__(self):
        return f'{self.name_en}'


class Invoice(CompanyMixins):
    customer = models.ForeignKey(CustomerDetail, on_delete=models.CASCADE, related_name="invoice")
    currency = models.ForeignKey(CurrencyCodes, on_delete=models.CASCADE, null=True, related_name="invoice_currency")
    payment_terms = models.ForeignKey(PaymentTerms, on_delete=models.CASCADE, null=True,
                                      related_name="invoice_payment_terms")
    uuid = models.UUIDField(null=True, blank=True)
    serial_no = models.CharField(max_length=255, verbose_name="Invoice Number", blank=True, null=True)
    hash = models.CharField(null=True, blank=True, max_length=500)
    date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    payment_method = models.TextField(null=True, blank=True, choices=PaymentMethodsChoices.choices)
    icv = models.CharField(max_length=10, null=True, blank=True)
    document_types = models.CharField(null=True, blank=True, max_length=500, choices=InvoiceType.choices)
    transaction_type = models.CharField(null=True, blank=True, max_length=500, choices=TransactionType.choices)
    transaction_status = models.CharField(null=True, blank=True, max_length=150,
                                          choices=TransactionStatusChoices.choices)
    invoice_lines = JSONField(null=True, blank=True)
    xml_string = models.TextField(null=True, blank=True)
    status_code = models.CharField(null=True, blank=True, max_length=500)
    status_response = models.TextField(null=True, blank=True, max_length=1500)
    invoice_qrcode = models.CharField(null=True, blank=True, max_length=1000)
    tax_inclusive = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    is_return = models.BooleanField(default=False, verbose_name="Return Invoice")
    extra_data = models.JSONField(null=True, blank=True)
    objects = DefaultManager()

    def __str__(self):
        return f'{self.serial_no}'


class ProductInvoice(CompanyMixins):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True, related_name="transaction")
    item = models.ForeignKey(ProductItems, on_delete=models.CASCADE, null=True, related_name="invoice")
    tax_type = models.ForeignKey(TaxType, on_delete=models.CASCADE, null=True, blank=True, related_name="tax_value")
    description = models.TextField(null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_inclusive_tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    objects = DefaultManager()

    def __str__(self):
        return f'{self.invoice} - {self.item}'


class PaymentHistory(TimeStampMixins):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payment_history')
    payment_plan = models.ForeignKey(SubscriptionPlan, null=True, blank=True, on_delete=models.CASCADE)
    orderID = models.CharField(max_length=100, null=True, blank=True)
    payerID = models.CharField(max_length=100, null=True, blank=True)
    paymentID = models.CharField(max_length=100, null=True, blank=True)
    billingToken = models.CharField(max_length=100, blank=True, null=True)
    facilitatorAccessToken = models.CharField(max_length=200, blank=True, null=True)
    paymentSource = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    status = (("pending", "Pending"), ("success", "success"), ("failed", "failed"))
    status = models.CharField(max_length=100, null=True, blank=True, default="pending", choices=status)
    objects = DefaultManager()

    def __str__(self):
        return self.orderID


def xml_string(data):
    return """<cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyIdentification>
                <cbc:ID schemeID='""" + str(data.get('schemaType', '') or '') + """'>""" + str(
        data.get('schemaNo', '') or '') + """</cbc:ID>
            </cac:PartyIdentification>
            <cac:PostalAddress>
                <cbc:StreetName>""" + str(data.get('streetName') or '') + """</cbc:StreetName>
                <cbc:BuildingNumber>""" + str(data.get('buildingNumber') or '') + """</cbc:BuildingNumber>
                <cbc:PlotIdentification>""" + str(data.get('plotIdentification') or '') + """</cbc:PlotIdentification>
                <cbc:CitySubdivisionName>""" + str(data.get('citySubdivisionName') or '') + """</cbc:CitySubdivisionName>
                <cbc:CityName>""" + str(data.get('cityName') or '') + """</cbc:CityName>
                <cbc:PostalZone>""" + str(data.get('postalZone') or '') + """</cbc:PostalZone>
                <cac:Country>
                    <cbc:IdentificationCode>SA</cbc:IdentificationCode>
                </cac:Country>
            </cac:PostalAddress>
            <cac:PartyTaxScheme>
                <cbc:CompanyID>""" + str(data.get('companyID') or '') + """</cbc:CompanyID>
                <cac:TaxScheme>
                    <cbc:ID>""" + str(data.get('taxID') or '') + """</cbc:ID>
                </cac:TaxScheme>
            </cac:PartyTaxScheme>
            <cac:PartyLegalEntity>
                <cbc:RegistrationName>""" + str(data.get('registrationName') or '') + """</cbc:RegistrationName>
            </cac:PartyLegalEntity>
        </cac:Party>
    </cac:AccountingSupplierParty>"""


# customer xml
def customer_xml(data):
    return """<cac:AccountingCustomerParty>
    <cac:Party>
        <cac:PostalAddress>
            <cbc:StreetName>""" + (data.get('streetName') or '') + """</cbc:StreetName>
            <cbc:BuildingNumber>""" + (data.get('buildingNumber') or '') + """</cbc:BuildingNumber>
            <cbc:CitySubdivisionName>""" + (data.get('citySubdivisionName') or '') + """</cbc:CitySubdivisionName>
            <cbc:CityName>""" + (data.get('cityName') or '') + """</cbc:CityName>
            <cbc:PostalZone>""" + (data.get('postalZone') or '') + """</cbc:PostalZone>
            <cac:Country>
                <cbc:IdentificationCode>SA</cbc:IdentificationCode>
            </cac:Country>
        </cac:PostalAddress>
        <cac:PartyTaxScheme>
            <cbc:CompanyID>""" + (data.get('companyID') or '') + """</cbc:CompanyID>
            <cac:TaxScheme>
                <cbc:ID>""" + (data.get('taxID') or '') + """</cbc:ID>
            </cac:TaxScheme>
        </cac:PartyTaxScheme>
        <cac:PartyLegalEntity>
            <cbc:RegistrationName>""" + (data.get('registrationName') or '') + """</cbc:RegistrationName>
        </cac:PartyLegalEntity>
    </cac:Party>
</cac:AccountingCustomerParty>"""


@receiver(post_save, sender=SupplierDetails, dispatch_uid="update_xml_text")
def update_xml_text_signal(sender, instance, created, **kwargs):
    xml_data = {
        'schemaType': instance.scheme_type, 'schemaNo': instance.scheme_no,
        'streetName': instance.scheme_no,
        'buildingNumber': instance.building_number,
        # 'plotIdentification': instance.plot_identification,
        'citySubdivisionName': instance.city_subdivision_name,
        'cityName': instance.city_name,
        'postalZone': instance.postal_zone,
        'companyID': instance.company.csr.tax_no,
        'taxID': instance.tax_scheme,
        'registrationName': instance.company.csr.organisation,
    }

    xml_result = xml_string(xml_data)

    if created or instance.xml_text != xml_result:
        instance.xml_text = xml_result
        instance.save()


@receiver(post_save, sender=CustomerDetail, dispatch_uid="updated_xml_text")
def update_xml_text_signal(sender, instance, created, **kwargs):
    xml_data = {
        'streetName': (instance.street_name or "صلاح الدين | Salah Al-Din"),
        'buildingNumber': (instance.building_number or "1111"),
        'citySubdivisionName': (instance.city_subdivision_name or "المروج | Al-Murooj"),
        'cityName': (instance.city or "الرياض | Riyadh"),
        'postalZone': (instance.postal_code or "12222"),
        'companyID': (instance.vat_no or "399999999800003"),
        'taxID': (instance.license_type or "VAT"),
        'registrationName': (instance.registered_name or "شركة نماذج فاتورة المحدودة | Fatoora Samples LTD"),
    }

    xml_result = customer_xml(xml_data)

    if created or instance.xml_text != xml_result:
        instance.xml_text = xml_result
        instance.save()


@receiver(post_save, sender=Company, dispatch_uid="company_create_defaults")
def company_create_signal(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            if not UnitOfMeasurements.objects.filter(company=instance).exists():
                UnitOfMeasurements.objects.bulk_create([
                    UnitOfMeasurements(company=instance, name="Unit", unit_value=1),
                    UnitOfMeasurements(company=instance, name="Packet", unit_value=2),
                    UnitOfMeasurements(company=instance, name="K.G", unit_value=3),
                    UnitOfMeasurements(company=instance, name="Gram", unit_value=4),
                    UnitOfMeasurements(company=instance, name="Dozen", unit_value=12),
                ])
            if not Category.objects.filter(company=instance).exists():
                Category.objects.create(company=instance, name="General",
                                        description="Default category for general products and services")


            if not CurrencyCodes.objects.filter(company=instance).exists():
                CurrencyCodes.objects.bulk_create([
                    CurrencyCodes(company=instance, code="USD", name="United States Dollar", symbol="$"),
                    CurrencyCodes(company=instance, code="SAR", name="Saudi Riyal", symbol="﷼"),
                    CurrencyCodes(company=instance, code="AED", name="UAE Dirham", symbol="د.إ"),
                    CurrencyCodes(company=instance, code="QAR", name="Qatari Riyal", symbol="ر.ق"),
                    CurrencyCodes(company=instance, code="OMR", name="Omani Rial", symbol="ر.ع."),
                    CurrencyCodes(company=instance, code="KWD", name="Kuwaiti Dinar", symbol="د.ك"),
                    CurrencyCodes(company=instance, code="BHD", name="Bahraini Dinar", symbol=".د.ب"),
                    CurrencyCodes(company=instance, code="EGP", name="Egyptian Pound", symbol="£"),
                ])


            if not TaxType.objects.filter(company=instance).exists():
                TaxType.objects.bulk_create([
                    TaxType(company=instance, name="EXEMPT", tax_percentage=Decimal("0"), vat_group="DOMESTIC", description="EXEMPT", tax_category="E"),
                    TaxType(company=instance, name="EXP", tax_percentage=Decimal("15"), vat_group="DOMESTIC", description="Expenses (15 %)", tax_category="S"),
                    TaxType(company=instance, name="NON TAXABLE", tax_percentage=Decimal("0"), vat_group="DOMESTIC", description="Non TaableZero (0 %)", tax_category="Z"),
                    TaxType(company=instance, name="STANDARD", tax_percentage=Decimal("15"), vat_group="DOMESTIC", description="STANDARD (15 %)", tax_category="S"),
                    TaxType(company=instance, name="EXPORT", tax_percentage=Decimal("0"), vat_group="FOREIGN", description="EXPORT", tax_category="G"),
                    TaxType(company=instance, name="FOREIGN SERVICES", tax_percentage=Decimal("0"), vat_group="FOREIGN", description="FOREIGN SERVICES", tax_category="Z"),
                    TaxType(company=instance, name="IMPORT", tax_percentage=Decimal("0"), vat_group="FOREIGN", description="IMPORT", tax_category="Z"),
                    TaxType(company=instance, name="NON TAXABLE", tax_percentage=Decimal("0"), vat_group="FOREIGN", description="Non TaableZero (0 %)", tax_category="Z"),
                    TaxType(company=instance, name="STANDARD", tax_percentage=Decimal("15"), vat_group="FOREIGN", description="STANDARD (15 %)", tax_category="Z"),
                ])






