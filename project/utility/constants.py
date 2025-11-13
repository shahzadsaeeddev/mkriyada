from django.db import models


class PaymentMethodsChoices(models.TextChoices):
    CASH = "10", "Cash,نقدي"
    CHEQUE = "20", "Cheque,شيك"
    CREDIT = "30", "Credit,ذمم"
    BANK_TRANSFER = "42", "Bank Transfer,حوالة بنكية"
    BANK_CARD = "48", "Bank Card, Visa Mada"
    OTHER = "1", "Instrument not defined,اخرى"


class InvoiceType(models.TextChoices):
    STANDARD_INVOICE = "Standard_invoice", "Standard Invoice"
    STANDARD_CREDIT_NOTE = "Standard_credit_note", "Standard Credit Note"
    STANDARD_DEBIT_NOTE = "Standard_debit_note", "Standard Debit Note"
    SIMPLIFIED_INVOICE = "Simplified_invoice", "Simplified Invoice"
    SIMPLIFIED_CREDIT_NOTE = "Simplified_credit_note", "Simplified Credit Note"
    SIMPLIFIED_DEBIT_NOTE = "Simplified_debit_note", "Simplified Debit Note"


class TransactionType(models.TextChoices):
    SALE = 'sale', "Sale"
    CREDIT_NOTE = 'credit_note', "Credit Note"
    DEBIT_NOTE = 'debit_note', "Debit Note"


class TransactionStatusChoices(models.TextChoices):
    PENDING = "PENDING", "PENDING"
    PROCESSING = "PROCESSING", "PROCESSING"
    COMPLETED = "COMPLETED", "COMPLETED"
    REJECTED = "REJECTED", "REJECTED"
    CANCELLED = "CANCELLED", "CANCELED"


class CompanyActionChoices(models.TextChoices):
    EXTEND = "extend", "Extend"
    SUSPEND = "suspend", "Suspend"
    REACTIVATE = "reactivate", "Reactivate"


class CompanyPhaseChoices(models.TextChoices):
    PHASE1 = "1", "Phase 1"
    PHASE2 = "2", "Phase 2"


class CompanyPortalChoices(models.TextChoices):
    SANDBOX = "sandbox", "Sandbox"
    PRODUCTION = "production", "Production"