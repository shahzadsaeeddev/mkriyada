import uuid
from datetime import datetime, timedelta

from django.db import transaction
from rest_framework import serializers
from .Commons import BusinessLocationsSerializer, SupplierEgsSerializer
from .Subscription import SubscriptionSerializer
from ..csr.csr_generator import create_csr
from ..models import SubscriptionPlan, EgsLocations, SupplierDetails, Sandbox, Production, Company
from accounts.keycloak import update_role_self
from accounts.models import Users


class CompanyPlanSerializer(serializers.ModelSerializer):
    plan = SubscriptionSerializer()
    next_plan = serializers.SerializerMethodField()

    def get_next_plan(self, obj):
        plan = obj.plan
        if not plan:
            return None
        next_plan = SubscriptionPlan.objects.filter(price__gt=plan.price).order_by('price').first()

        if next_plan:
            return SubscriptionSerializer(next_plan).data
        return None

    class Meta:
        model = Company
        fields = ['expiry', 'plan', 'next_plan']


class CompanySerializer(serializers.ModelSerializer):
    has_csid = serializers.SerializerMethodField()
    has_x509 = serializers.SerializerMethodField()
    is_simplified_invoice = serializers.SerializerMethodField()
    is_simplified_debit_note = serializers.SerializerMethodField()
    is_simplified_credit_note = serializers.SerializerMethodField()
    is_standard_invoice = serializers.SerializerMethodField()
    is_standard_debit_note = serializers.SerializerMethodField()
    is_standard_credit_note = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'api_key', 'secret_key', 'has_csid', 'has_x509',
            'is_simplified_invoice', 'is_simplified_debit_note', 'is_simplified_credit_note',
            'is_standard_invoice', 'is_standard_debit_note', 'is_standard_credit_note'
        ]

    def get_has_csid(self, obj):
        return bool(getattr(obj.production, 'csid', None))

    def get_has_x509(self, obj):
        return bool(getattr(obj.production, 'x509_certificate', None))

    def get_is_simplified_invoice(self, obj):
        return obj.production.is_simplified_invoice if hasattr(obj, 'production') else False

    def get_is_simplified_debit_note(self, obj):
        return obj.production.is_simplified_debit_note if hasattr(obj, 'production') else False

    def get_is_simplified_credit_note(self, obj):
        return obj.production.is_simplified_credit_note if hasattr(obj, 'production') else False

    def get_is_standard_invoice(self, obj):
        return obj.production.is_standard_invoice if hasattr(obj, 'production') else False

    def get_is_standard_debit_note(self, obj):
        return obj.production.is_standard_debit_note if hasattr(obj, 'production') else False

    def get_is_standard_credit_note(self, obj):
        return obj.production.is_standard_credit_note if hasattr(obj, 'production') else False


class CompanyUpdateSerializer(serializers.ModelSerializer):
    csr = BusinessLocationsSerializer(required=False)
    supplier = SupplierEgsSerializer(required=False)
    thumbnail = serializers.FileField(source='media_file.file', required=False, read_only=True)

    class Meta:
        model = Company
        exclude = ['updated_at', 'api_key', 'secret_key', 'plan', 'expiry', 'action', 'max_users',
                   'max_invoices', 'enabled_zatca', 'sandbox_secret_key']

        extra_kwargs = {
            'media_file': {'write_only': True},
        }

    def update(self, instance, validated_data):
        csr_data = validated_data.pop("csr", None)
        supplier_data = validated_data.pop("supplier", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if csr_data is not None:
            csr_instance, _ = EgsLocations.objects.update_or_create(
                company=instance,
                defaults=csr_data
            )
            instance.csr = csr_instance

        if supplier_data is not None:
            supplier_instance, _ = SupplierDetails.objects.update_or_create(
                company=instance,
                defaults=supplier_data
            )
            instance.supplier = supplier_instance

        return instance


class CompanyCreateSerializer(serializers.ModelSerializer):
    thumbnail = serializers.FileField(source='media_file.file', required=False, read_only=True)
    csr = BusinessLocationsSerializer()
    supplier = SupplierEgsSerializer()

    class Meta:
        model = Company
        exclude = ['updated_at', 'api_key', 'secret_key', 'sandbox_secret_key', 'plan', 'expiry', 'action', 'max_users',
                   'max_invoices', 'enabled_zatca']
        extra_kwargs = {
            'media_file': {'write_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        if user.company:
            raise serializers.ValidationError("You already have a company")

        csr_data = validated_data.pop('csr', None)
        supplier_data = validated_data.pop('supplier', None)

        with transaction.atomic():
            expiry_date = datetime.now().date() + timedelta(days=30)
            plan = SubscriptionPlan.objects.filter(default=True).first()
            company = Company.objects.create(**validated_data, plan=plan, expiry=expiry_date,
                                             max_users=plan.number_of_users, max_invoices=plan.invoice_limit)

            company_name = (company.name[:3].upper())
            scheme_no = str(supplier_data.get("scheme_no"))
            tax_no = csr_data.get("tax_no")
            common_name = f"{company_name}-{scheme_no}-{tax_no}"

            if csr_data:
                serial_no = f"1-mkriyada|2- version 2.0 |3-{uuid.uuid4()}"

                location = EgsLocations.objects.create(company=company, serial_number=serial_no,
                                                       common_name=common_name, organisation=company.name, **csr_data)

            if supplier_data:
                SupplierDetails.objects.create(company=company, city_subdivision_name=company.district,
                                               city_name=company.city, **supplier_data)

            user = self.context['request'].user

            Users.objects.filter(id=user.id).update(company=company)
            user.company = company

            request = self.context.get('request')
            auth_header = request.META.get('HTTP_AUTHORIZATION', None)
            if not auth_header or not auth_header.startswith("Bearer "):
                raise serializers.ValidationError("Authorization token missing")

            auth_token = auth_header.split(" ")[1]

            try:
                user_id, assigned = update_role_self(auth_token, user.username, company.name, company.enabled_zatca)
                user.user_roles = assigned
                user.save(update_fields=["user_roles"])

            except Exception as e:
                raise e

            if location:
                organisation = location.organisation[:50]
                csr_sandbox_response = create_csr(OU=location.organisation_unit, O=organisation,
                                                  CN=location.common_name,
                                                  SN=location.serial_number, UID=location.tax_no, title=location.title,
                                                  registeredAddress=location.registered_address,
                                                  business=location.business_category, TYPE='TSTZATCA-Code-Signing')

                csr_response = create_csr(OU=location.organisation_unit, O=organisation,
                                          CN=location.common_name, SN=location.serial_number,
                                          UID=location.tax_no, title=location.title,
                                          registeredAddress=location.registered_address,
                                          business=location.business_category,
                                          TYPE='ZATCA-Code-Signing')

                if csr_sandbox_response.get('status') != 200:
                    raise serializers.ValidationError("CSR generation failed")

                Sandbox.objects.create(company=company, csr=csr_sandbox_response.get('csr'),
                                       private_key=csr_sandbox_response.get('pvt'),
                                       public_key=csr_sandbox_response.get('pbl'))

                Production.objects.create(company=company, csr=csr_response.get('csr'),
                                          private_key=csr_response.get('pvt'),
                                          public_key=csr_response.get('pbl'), )

        return company

    def update(self, instance, validated_data):
        csr_data = validated_data.pop("csr", None)
        supplier_data = validated_data.pop("supplier", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        csr_instance = None
        if csr_data is not None:
            csr_instance, _ = EgsLocations.objects.update_or_create(
                company=instance,
                defaults=csr_data
            )
            instance.csr = csr_instance

        if supplier_data is not None:
            supplier_instance, _ = SupplierDetails.objects.update_or_create(
                company=instance,
                defaults=supplier_data
            )
            instance.supplier = supplier_instance

        user = self.context['request'].user

        Users.objects.filter(id=user.id).update(company=instance)
        user.company = instance

        request = self.context.get('request')
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header or not auth_header.startswith("Bearer "):
            raise serializers.ValidationError("Authorization token missing")

        auth_token = auth_header.split(" ")[1]

        update_role_self(auth_token, user.username, instance.name, instance.enabled_zatca)

        return instance



class CompanyMasterAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name']
