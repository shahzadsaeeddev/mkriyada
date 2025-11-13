import base64
import json

from rest_framework import serializers

from ..models import EgsLocations, SupplierDetails, Country

from ..csr.csid_create import generate_csid, generate_x509
from ..models import Production
from ..zatca_operations.zatca import Zatca


class BusinessLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EgsLocations
        exclude = ['updated_at']


class SupplierEgsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierDetails
        exclude = ['updated_at', 'xml_text']


class LocationSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='seller_name', read_only=True)
    otp = serializers.CharField(write_only=True, required=False, max_length=6)
    x509 = serializers.CharField(write_only=True, required=False, max_length=6)

    # def get_production(self, instance):
    #     return {
    #         "csr": bool(instance.production.csr),
    #         "csid": bool(instance.production.csid),
    #         "x509": bool(instance.production.x509_certificate)
    #     }

    class Meta:
        model = EgsLocations
        exclude = ['branch', 'seller_name', 'tax_no', 'common_name', "schemeType", "schemeNo", "StreetName", "BuildingNumber", "PlotIdentification", "CitySubdivisionName", "CityName", "PostalZone"]
        # extra_kwargs = {'authentication_token': {'read_only': True}}

    def update(self, instance, validated_data):



        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if validated_data['enable_zatca']:
            zatca = Zatca(instance.id)
            csr_response = zatca.generate_csr()
            # if csr_response:
            #     Sandbox.objects.get_or_create(
            #         location=instance,
            #         defaults={
            #             'csr': csr_response.get('csr'),
            #             'private_key': csr_response.get('pvt'),
            #             'public_key': csr_response.get('pbl'),
            #             'csid': None,
            #             'csid_base64': None,
            #             'secret_csid': None,
            #             'csid_request': None,
            #             'x509_base64': None,
            #             'x509_certificate': None,
            #             'x509_secret': None,
            #             'x509_request': None,
            #         }
            #     )





        instance.save()
        return instance

    def create(self, validated_data):
        location = EgsLocations.objects.create(**validated_data)
        if location.enable_zatca:
            zatca = Zatca(location.id)
            csr_response = zatca.generate_csr()

        return location


class BusinessLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EgsLocations
        fields = ["schemeType", "schemeNo", "StreetName", "BuildingNumber", "PlotIdentification", "CitySubdivisionName", "CityName", "PostalZone", "TaxScheme"]

class LocationListSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='seller_name', read_only=True)
    class Meta:
        model = EgsLocations
        exclude = ['seller_name', 'tax_no', 'common_name']

class CSIDSeliazer(serializers.Serializer):
    scope = serializers.CharField(max_length=250)
    otp = serializers.IntegerField()


class ProductionSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Production
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_csid(instance.csr, validated_data['otp'], 'production')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.csid = result['binarySecurityToken']
        instance.csid_base64 = base64.b64decode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.secret_csid = result['secret']
        instance.csid_request = result['requestID']
        instance.save()
        return instance


class ProductionX509Serializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Production
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_x509(instance.csid, instance.secret_csid, instance.csid_request, 'production')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.x509_base64 = base64.b64decode(bytes(result['data']['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.x509_certificate = result['binarySecurityToken']
        instance.x509_secret = result['secret']
        instance.x509_request = result['requestID']
        instance.save()
        return instance


class ComplainceSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(max_length=6, required=True, write_only=True)

    class Meta:
        model = Production
        fields = ['otp']

    def update(self, instance, validated_data):
        result = generate_x509(instance.csid, instance.secret_csid, instance.csid_request, 'production')
        if result.status_code != 200:
            raise serializers.ValidationError(result.text)
        result = json.loads(result.text)
        instance.x509_base64 = base64.b64encode(bytes(result['binarySecurityToken'], 'utf-8')).decode('utf-8')
        instance.x509_certificate = result['binarySecurityToken']
        instance.x509_secret = result['secret']
        instance.x509_request = result['requestID']
        instance.save()
        return instance



class BusinessLocationsUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = EgsLocations
        exclude = ['updated_at']



class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'short_name', 'country_code']
