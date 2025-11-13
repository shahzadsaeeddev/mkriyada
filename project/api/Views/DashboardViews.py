import calendar
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db.models.aggregates import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Users

from ..Serializers.DashboardSerializers import InvoiceReportingLogsSerializer, SubscriptionInvoicesSerializer
from ..models import Invoice, ProductInvoice, PaymentHistory, Company
from product.models import ActivityLog
from accounts.permissions import HasUserDashboardRole, HasAnalyticsRole, HasAdminDashboardRole


class AdminDashboardApiView(APIView):
    permission_classes = [HasAdminDashboardRole]

    def get(self, request):
        today = date.today()
        start_date = today.replace(day=1) - relativedelta(months=5)

        monthly_sales_qs = (
            PaymentHistory.objects.filter(created_at__gte=start_date)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("payment_plan__price"))
            .order_by("month")
        )

        db_data = {entry["month"].strftime("%Y-%m"): entry["total"] or 0 for entry in monthly_sales_qs}

        monthly_sales = [
            {
                "month": (start_date + relativedelta(months=i)).strftime("%b"),
                "total": db_data.get((start_date + relativedelta(months=i)).strftime("%Y-%m"), 0)
            }
            for i in range(6)
        ]

        activity_logs = ActivityLog.objects.values("module").annotate(count=Count("id")).order_by("-count")[:4]

        top_companies = Invoice.objects.filter(transaction_type="sale").values("company__name").annotate(
            total=Sum("sub_total")
        ).order_by("company__name")[:4]

        customers = Company.objects.filter(created_at__month=today.month).count()

        active_users = Users.objects.filter(is_active=True, company__isnull=False).count()
        expired_users = Users.objects.filter(is_active=False, company__isnull=False).count()
        invoice = Invoice.objects.all()[:4]
        subscription_invoice = SubscriptionInvoicesSerializer(invoice, many=True).data

        return Response({
            'active_users': active_users,
            'expired_users': expired_users,
            "subscription": monthly_sales,
            "company": top_companies,
            "customers": customers,
            "activity_logs": activity_logs,
            "invoice": subscription_invoice,
        })


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now

from api.models import Invoice, ProductInvoice


class UserDashboardApiView(APIView):
    permission_classes = [HasUserDashboardRole]

    def get_company_filter(self, request):

        user = request.user
        if user.user_roles and user.user_roles.group_name == "Owner":
            return None
        return user.company

    def get(self, request):
        company = self.get_company_filter(request)
        current_year = now().year
        today = date.today()
        start_date = today.replace(day=1) - relativedelta(months=5)

        invoice_filter = Q(transaction_type="sale", date__gte=start_date)
        if company:
            invoice_filter &= Q(company=company)

        monthly_sales_qs = (
            Invoice.objects.filter(invoice_filter)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Sum("total_amount"))
            .order_by("month")
        )
        db_data = {entry["month"].strftime("%Y-%m"): entry["total"] or 0 for entry in monthly_sales_qs}

        monthly_sales = [
            {
                "month": (start_date + relativedelta(months=i)).strftime("%b"),
                "total": db_data.get((start_date + relativedelta(months=i)).strftime("%Y-%m"), 0)
            }
            for i in range(6)
        ]

        invoice_filter_base = Q()
        if company:
            invoice_filter_base &= Q(company=company)

        queryset = (
            Invoice.objects.filter(invoice_filter_base)
            .values("document_types")
            .annotate(
                reported=Count("id", filter=Q(status_code="REPORTED")),
                not_reported=Count("id", filter=Q(status_code="NOT_REPORTED")),
                cleared=Count("id", filter=Q(status_code="CLEARED")),
                not_cleared=Count("id", filter=Q(status_code="NOT_CLEARED")),
            )
            .order_by("document_types")
        )

        data = [
            {
                "document_types": item["document_types"],
                "counts": {
                    "reported": item["reported"],
                    "not_reported": item["not_reported"],
                    "cleared": item["cleared"],
                    "not_cleared": item["not_cleared"],
                },
            }
            for item in queryset
        ]

        invoices_qs = Invoice.objects.all()
        if company:
            invoices_qs = invoices_qs.filter(company=company)

        invoices = invoices_qs.count()
        invoice_value = invoices_qs.aggregate(sub_total=Sum("sub_total")) or {"sub_total": 0}
        value = invoice_value["sub_total"] or 0

        product_qs = ProductInvoice.objects.filter(invoice__transaction_type="sale")
        if company:
            product_qs = product_qs.filter(invoice__company=company)

        top_products = (
            product_qs
            .values("item__name")
            .annotate(total_sales=Sum("total"))
            .order_by("-total_sales")[:5]
        )

        customer_qs = Invoice.objects.all()
        if company:
            customer_qs = customer_qs.filter(company=company)

        top_customers = (
            customer_qs
            .values("customer__name_en")
            .annotate(total=Sum("sub_total"))
            .order_by("-total")[:5]
        )

        return Response({
            "data": data,
            "invoices": invoices,
            "invoice_value": value,
            "top_products": top_products,
            "top_customers": top_customers,
            "sale_trend": monthly_sales,
        })



class AnalyticsLogsApiView(APIView):
    permission_classes = [HasAnalyticsRole]

    def get_company_filter(self, user):

        if user.is_superuser or (user.user_roles and user.user_roles.group_name == "Owner"):
            return Q()
        return Q(company=user.company)

    def get(self, request):
        user = request.user
        company_filter = self.get_company_filter(user)
        current_year = now().year

        stats = Invoice.objects.filter(company_filter).aggregate(
            total_invoices=Count("id"),
            reported_invoices=Count("id", filter=Q(status_code="REPORTED")),
            not_reported_invoices=Count("id", filter=Q(status_code="NOT_REPORTED")),
            not_cleared_invoices=Count("id", filter=Q(status_code="NOT_CLEARED")),
        )

        monthly_sales_qs = (
            Invoice.objects.filter(company_filter, status_code="REPORTED", date__year=current_year)
            .annotate(month=TruncMonth("date"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        db_data = {entry["month"].month: entry["total"] or 0 for entry in monthly_sales_qs}

        monthly_reporting = [
            {"month": calendar.month_name[m][:3], "total": db_data.get(m, 0)}
            for m in range(1, 13)
        ]

        transactions = Invoice.objects.filter(company_filter).aggregate(
            sale=Sum("sub_total", filter=Q(transaction_type="sale")),
            credit_note=Sum("sub_total", filter=Q(transaction_type="credit_note")),
            debit_note=Sum("sub_total", filter=Q(transaction_type="debit_note")),
        )

        transactions_list = [
            {"type": key, "total": transactions[key] or 0}
            for key in ["sale", "credit_note", "debit_note"]
        ]

        status = Invoice.objects.filter(company_filter).aggregate(
            cleared=Count("id", filter=Q(status_code="CLEARED")),
            not_cleared=Count("id", filter=Q(status_code="NOT_CLEARED")),
        )

        reporting_status = Invoice.objects.filter(company_filter).aggregate(
            cleared=Count("id", filter=Q(status_code="REPORTED")),
            not_cleared=Count("id", filter=Q(status_code="NOT_REPORTED")),
        )

        status_list = [
            {"type": key, "total": status[key] or 0} for key in ["cleared", "not_cleared"]
        ]

        invoice_log = Invoice.objects.filter(company_filter).order_by("-created_at")[:10]
        invoice_logs = InvoiceReportingLogsSerializer(invoice_log, many=True).data

        return Response({
            "logs": stats,
            "reporting": monthly_reporting,
            "transactions": transactions_list,
            "status": status_list,
            "invoice_logs": invoice_logs,
            "reporting_status": reporting_status,
        })
