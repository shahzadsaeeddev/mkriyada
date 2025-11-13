from datetime import datetime
from decimal import Decimal

from django.db.models import Sum, Q, Count, F
from django.db.models.functions import TruncDate, TruncMonth
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .CompanyMixins import CompanyQuerysetMixin
from ..models import Invoice, ProductInvoice, Company
from ..Serializers.ReportsSerializers import SaleReportSerializer, ProductReportSerializer, CustomerReportSerializer, \
    ZatcaSubmissionReportSerializer, SalesByCategorySerializer, TopCustomersSerializer, \
    CustomerSalesTrendSerializer, SalesGrowthTrendSerializer, ItemSalesTrendSerializer, TaxSalesReportSerializer, \
    DocumentTypeReportSerializer, SubscriptionPlanReportSerializer, SystemReportSerializer
from product.models import ProductItems

from accounts.permissions import HasReportRole, HasAdminReportsRole


class ReportsApiView(CompanyQuerysetMixin, APIView):
    permission_classes = [HasReportRole]

    def get_queryset(self):
        return Invoice.objects.filter(company=self.get_company())

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        prefix = request.query_params.get('report')
        period = request.query_params.get('period', 'month')

        queryset = self.get_queryset()
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        # ---------------------- Base Reports ----------------------
        if prefix == 'sale':
            return Response(SaleReportSerializer(queryset.filter(transaction_type="sale"), many=True).data)

        elif prefix == 'detail_invoice':
            return Response(SaleReportSerializer(queryset, many=True).data)

        elif prefix == 'debit_credit':
            return Response(
                SaleReportSerializer(
                    queryset.filter(transaction_type__in=["credit_note", "debit_note"]),
                    many=True
                ).data
            )

        elif prefix == 'zatca':
            return Response(ZatcaSubmissionReportSerializer(queryset.filter(document_types__isnull=False), many=True).data)




        elif prefix == "product":

            products = ProductInvoice.objects.filter(company=self.get_company(),invoice__transaction_type="sale")

            if start_date and end_date:
                products = products.filter(invoice__date__range=[start_date, end_date])
            total_sales = products.aggregate(total=Sum(F("quantity") * F("price"))).get("total") or 0
            serializer = ProductReportSerializer(products.order_by("-invoice__date")[:10], many=True, context={"total_sales": total_sales})

            return Response(serializer.data)


        elif prefix == 'customer':
            return Response(CustomerReportSerializer(queryset, many=True).data)

        # ---------------------- Trend Reports ----------------------
        if prefix == "item_sales_trend":
            trunc = TruncDate("invoice__date") if period == "day" else TruncMonth("invoice__date")
            data = ProductInvoice.objects.filter(company=self.get_company(), invoice__is_return=False).annotate(
                period=trunc).values("period", "item__name").annotate(total_quantity=Sum("quantity"),
                                                                      total_sales=Sum("total")).order_by("period",
                                                                                                         "item__name")

            return Response(ItemSalesTrendSerializer(data, many=True).data)

            # ---------------------- SALES GROWTH TREND ----------------------
        if prefix == "sales_growth_trend":
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                diff_days = (end - start).days

                trunc = TruncDate("date") if diff_days <= 31 else TruncMonth("date")
            else:
                trunc = TruncMonth("date")

            grouped = (
                queryset.annotate(period=trunc)
                .values("period")
                .annotate(sales_value=Sum("total_amount"))
                .order_by("period")
            )

            data = []
            prev_sales = Decimal(0)
            for row in grouped:
                current_sales = row["sales_value"] or Decimal(0)
                if prev_sales == 0:
                    growth = Decimal(0)
                else:
                    growth = ((current_sales - prev_sales) / prev_sales) * 100
                row["growth_percent"] = round(growth, 2)
                data.append(row)
                prev_sales = current_sales

            serializer = SalesGrowthTrendSerializer(data, many=True)
            return Response(serializer.data)


        # ---------------------- CUSTOMER SALES TREND ----------------------
        elif prefix == "customer_sales_trend":
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")

            queryset = queryset.filter(is_return=False)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                diff_days = (end - start).days

                trunc = TruncDate("date") if diff_days <= 31 else TruncMonth("date")
            else:
                trunc = TruncMonth("date")

            data = (
                queryset.annotate(period=trunc)
                .values("period", "customer__name_en")
                .annotate(invoice_count=Count("id"), total_sales=Sum("total_amount"))
                .order_by("period", "customer__name_en")
            )

            serializer = CustomerSalesTrendSerializer(data, many=True)
            return Response(serializer.data)

            # ---------------------- TOP CUSTOMERS ----------------------
        elif prefix == "top_customers":
            invoices = queryset.filter(is_return=False)

            data = invoices.values("customer__name_en").annotate(invoice_count=Count("id"),
                                                                 total_sales=Sum("total_amount")).order_by(
                "-total_sales")[:10]

            total_sales_sum = sum(d["total_sales"] or 0 for d in data)

            serializer = TopCustomersSerializer(data, many=True, context={"total_sales_sum": total_sales_sum})
            return Response(serializer.data)

            # ---------------------- SALES BY CATEGORY ----------------------
        elif prefix == "sales_by_category":
            category_id = request.query_params.get("category_id")

            products = ProductInvoice.objects.filter(
                company=self.get_company(),
                invoice__is_return=False
            )

            if category_id:
                products = products.filter(item__category_id=category_id)

            data = (
                products.values("item__category__name")
                .annotate(
                    total_quantity=Sum("quantity"),
                    total_sales=Sum("total")
                )
                .order_by("-total_sales")
            )

            total_sales_sum = sum([d["total_sales"] or 0 for d in data])

            serializer = SalesByCategorySerializer(data, many=True, context={"total_sales_sum": total_sales_sum})
            return Response(serializer.data)


        # ---------------------- TAX SALES ----------------------
        elif prefix == "tax_sales":
            trunc = TruncDate("date") if period == "day" else TruncMonth("date")

            invoices = queryset.filter(is_return=False)

            data = (
                invoices
                .annotate(period=trunc)
                .values("period")
                .annotate(
                    taxable_sales=Sum(
                        "total_amount", filter=Q(tax_amount__gt=0)
                    ),
                    exempt_sales=Sum(
                        "total_amount", filter=Q(tax_amount=0)
                    ),
                    vat_value=Sum("tax_amount"),
                )
                .order_by("period")
            )

            for d in data:
                d["taxable_sales"] = d.get("taxable_sales") or 0
                d["exempt_sales"] = d.get("exempt_sales") or 0
                d["vat_value"] = d.get("vat_value") or 0

            serializer = TaxSalesReportSerializer(data, many=True)
            return Response(serializer.data)


        elif prefix == "document_type_report":

            document_type = request.query_params.get("document_type")

            if not document_type:
                return Response(None)

            invoices = queryset

            if document_type:
                invoices = invoices.filter(document_types=document_type)

            if start_date and end_date:

                start = datetime.strptime(start_date, "%Y-%m-%d").date()

                end = datetime.strptime(end_date, "%Y-%m-%d").date()

                diff_days = (end - start).days

                period_field = TruncDate("date") if diff_days <= 31 else TruncMonth("date")

            else:

                period_field = TruncMonth("date")

            data = invoices.annotate(period=period_field).values("period", "document_types").annotate(
                invoice_count=Count("id"), total_value=Sum("total_amount"), ).order_by("period", "document_types")


            if not data:
                return Response(None)

            serializer = DocumentTypeReportSerializer(data, many=True)
            return Response(serializer.data)

        # ---------------------- Invalid Report ----------------------
        else:
            return Response(
                {"error": "Invalid report type"},
                status=status.HTTP_400_BAD_REQUEST
            )



class SuperAdminReports(APIView):
    permission_classes = [HasAdminReportsRole]

    def get(self, request):
        prefix = request.query_params.get("report")
        if prefix == "sub_report":
            company = Company.objects.all()
            subscription_report = SubscriptionPlanReportSerializer(company, many=True).data
            return Response(subscription_report)

        elif prefix == "system_report":
            company = Company.objects.all()
            system_report = SystemReportSerializer(company, many=True).data
            return Response(system_report)


