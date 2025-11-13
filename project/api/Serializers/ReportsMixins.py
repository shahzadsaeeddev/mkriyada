from decimal import Decimal

from django.db.models import Sum, F

from ..models import ProductInvoice


class SaleReportMixins:
    def get_item(self, obj):
        item_name = obj.transaction.first()
        return item_name.item.name if item_name and item_name.item else None

    def get_discount(self, obj):
        journal_line = obj.transaction.first()
        if journal_line:
            return journal_line.discount if journal_line else None


class ProductReportMixins:

    def get_category_name(self, obj):
        product = obj.item
        if product:
            return product.category.name if product and product.category.name else None

    def get_qty_sold(self, obj):
        return (
                ProductInvoice.objects.filter(
                    item=obj.item,
                    company=obj.company,
                    invoice__is_return=False
                )
                .aggregate(total_qty=Sum('quantity'))
                .get('total_qty') or 0
        )

    # ✅ Compute total sales value for this product
    def get_sales_value(self, obj):
        return (
                ProductInvoice.objects.filter(
                    item=obj.item,
                    company=obj.company,
                    invoice__is_return=False
                )
                .aggregate(total_sales=Sum(F('quantity') * F('price')))
                .get('total_sales') or Decimal('0.00')
        )

    # ✅ Compute % of total sales
    def get_percentage_of_total(self, obj):
        total_sales = self.context.get('total_sales') or Decimal('0.00')
        product_sales = self.get_sales_value(obj)
        if total_sales > 0:
            percent = (product_sales / total_sales) * 100
            return round(percent, 2)
        return Decimal('0.00')



class CustomerReportMixins:
    def get_transaction_typ(self, obj):
        journal_line = obj.invoice.first()
        if journal_line:
            return journal_line.transaction_type if journal_line and journal_line.transaction_type else None

    def get_invoice_no(self, obj):
        journal_line = obj.invoice.first()
        if journal_line:
            return journal_line.serial_no if journal_line and journal_line.serial_no else None
