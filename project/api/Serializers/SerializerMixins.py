from num2words import num2words

from ..qrcode import generate_qrcode


class SandboxMixins:
    def index(self):
        pass


class QrCodeMixin:
    def get_qrcode_data(self, instance):
        return generate_qrcode(instance.company.name, instance.company.csr.tax_no,
                    str(instance.created_at.replace(tzinfo=None)), str(instance.total_amount),
                    str(instance.tax_amount))


class AmountInWordsMixins:
    def get_total_en(self, obj):
        try:
            amount = float(obj.total_amount)
            return num2words(amount, lang='en').title()
        except Exception:
            return None

    def get_total_ar(self, obj):
        try:
            amount = float(obj.total_amount)
            return num2words(amount, lang='ar')
        except Exception:
            return None


class SellerNumberMixin:
    def get_seller_no(self, obj):
        company = obj.company
        if company and company.csr.tax_no:
                if company.csr.tax_no:
                    return company.csr.tax_no
        return None



class SubscribersMixin:
    def get_name(self, instance):
        user = instance.users.first()
        return user.username

    def get_email(self, instance):
        user = instance.users.first()
        return user.email

