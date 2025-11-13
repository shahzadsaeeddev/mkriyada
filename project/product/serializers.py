from rest_framework import serializers

from .models import MediaFiles, Category, UnitOfMeasurements, ProductItems, NotificationCenter, ActivityLog, ItemTags


class MediaFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFiles
        fields = ['id', 'file_name', 'file', 'description', 'alt_text', 'thumbnail']
        read_only_fields = ['thumbnail']


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'media_file', 'description']
        extra_kwargs = {
            'media_file': {'write_only': True}
        }


class UnitOfMeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasurements
        fields = ['id', 'name', 'unit_value']



class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='umo.name', read_only=True)
    thumbnail = serializers.FileField(source='media_file.file', read_only=True)
    class Meta:
        model = ProductItems
        exclude = ['company', 'updated_at']
        extra_kwargs = {"media_file": {"write_only": True}}




class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationCenter
        fields = ['id', 'subject', 'message', 'recipient', 'channel', 'status']



class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        exclude = ['company', 'updated_at', 'ip_address']


class ItemTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemTags
        fields = ['id', 'name', 'description']

