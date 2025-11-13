from .Views.SubscribersViews import SubscriberListApiView
from .imports import *


app_name = 'api'
router = DefaultRouter()
router.register(r'locations', LocationView)

urlpatterns = [
    path('', Index, name='index'),
    # EGS Location Create post & patch
    path('egs-location/', BusinessLocationListCreateView.as_view(), name='egs-location'),
    path('egs-location-update/', BusinessLocationUpdateView.as_view(), name='egs-location'),

    # Supplier create post & patch
    path('supplier/', SupplierDetailsCreateApiView.as_view(), name='supplier'),
    path('supplier-update/', SupplierDetailsUpdateApiView.as_view(), name='supplier-update'),

    # customer detail
    path('customer/', CustomerListCreateApiView.as_view(), name='customer'),
    path('customer-detail/', CustomerDetailApiView.as_view(), name='customer-detail'),
    path('customer/<str:pk>/', CustomerRetrieveUpdateDeleteApiView.as_view(), name='customer'),

    #company
    path('company/', CompanyListApiView.as_view(), name='company'),
    path('company-create/', CompanyListCreateApiView.as_view(), name='company'),
    path('company-update/', CompanyUpdateApiView.as_view(), name='company'),
    path('master-account/', CompanyMasterAccountListApiView.as_view(), name='master-account'),


    # Payment Method
    path('create-payment-order/', CreatePaypalOrder.as_view(), name='create-orders'),
    path('capture-payment-order/', CapturePaypalOrder.as_view(), name='capture-payment'),

    # Current Company Plan
    path('company-plan/', CompanyPlanRetrieveView.as_view(), name='company-plan-detail'),
    path('subscription-plan/', SubscriptionPlanListView.as_view(), name='subscription-plan-list'),
    path('payment-history/', PaymentHistoryListView.as_view(), name='payment-history-list'),

    # Dashboard
    path('request-summery/', DashboardApiView.as_view(), name='request-summery'),


    # Production
    path('sale-list/', InvoicesProductionListApiView.as_view(), name='sale-list'),
    path('credit-list/', InvoicesProductionCreditListApiView.as_view(), name='sale-list'),
    path('debit-list/', InvoicesProductionDebitListApiView.as_view(), name='sale-list'),

    path('production/invoices-create/', InvoicesProductionApiView.as_view(), name='invoices-create'),
    path('production/credit-note/', InvoicesProductionCreditNoteApiView.as_view(), name='credit-note'),
    path('production/debit-note/', InvoicesProductionDebitNoteApiView.as_view(), name='debit-note'),
    path('production/validate-otp/', ProductionValidateOtpApiView.as_view(), name='validate-otp'),
    path('invoice-number/', ReturnInvoiceApiView.as_view(), name='invoice-number'),

    path('general-view/<str:pk>/', TransactionsGeneralView.as_view(), name='general-view'),

    path('sale-detail/<str:pk>/', SalePrintGeneralView.as_view(), name='sale-detail'),

    # Sandbox
    # path('invoices/', InvoicesListApiView.as_view(), name='invoices'),
    path('sandbox/invoices-create/', InvoicesSandboxApiView.as_view(), name='invoices-create'),
    path('sandbox/credit-note/', InvoicesSandboxCreditNoteApiView.as_view(), name='credit-note'),
    path('sandbox/debit-note/', InvoicesSandboxDebitNoteApiView.as_view(), name='debit-note'),
    path('sandbox/validate-otp/', ValidateOtpApiView.as_view(), name='debit-note'),
    path('sandbox/specific-credentials/', ValidateSpecificActionApiView.as_view(), name='debit-note'),
    path('sandbox/credentials/', SandboxCredentialsView.as_view(), name='debit-note'),

    path('resubmit-invoice/', ResubmitInvoiceAPIView.as_view(), name='resubmit-invoice'),

    # Serial Numbers
    path('code/', CustomerNoGenerateAPIView.as_view(), name="invoice-serial"),
    path('serial/', InvoiceSerialGenerateAPIView.as_view(), name="invoice-serial"),

    # Subscription Plans
    path('plans/', SubscriptionPlanListCreateView.as_view(), name='plan_list'),
    path('plans/<str:pk>/', SubscriptionPlanRetrieveUpdateDeleteView.as_view(), name='plan_list'),
    path('subscription-control/', SubscriptionControlApiView.as_view(), name='subscription-control'),

    path('init-transaction/', InitTransactionApiView.as_view(), name='init-transaction'),


    path('currency-code/', CurrencyCodeListCreateApiView.as_view(), name='currency-code'),
    path('payment-terms/', PaymentTermsListCreateApiView.as_view(), name='payment-terms'),
    # Reports

    # Dashboard
    path('admin-request-summery/', AdminDashboardApiView.as_view(), name='request-summery'),
    path('user-request-summery/', UserDashboardApiView.as_view(), name='user-request-summery'),
    path('analytics-logs/', AnalyticsLogsApiView.as_view(), name='analytics-logs'),




    path('countries/', CountryListView.as_view(), name='countries'),


    # Reports

    path('reports/', ReportsApiView.as_view(), name='reports'),
    path('admin-reports/', SuperAdminReports.as_view(), name='admin-reports'),

    # Subscribers

    path('subscribers/', SubscriberListApiView.as_view(), name='subscribers'),

    path('tax-types/', TaxTypeListCreateApiView.as_view(), name='tax-types'),
    path('tax-types/<str:pk>/', TaxTypeRetrieveUpdateApiView.as_view(), name='tax-types'),


]