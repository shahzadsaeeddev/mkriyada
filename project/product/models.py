from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from utility.modelMixins import CompanyMixins, TimeStampMixins, DefaultManager


class MediaFiles(CompanyMixins):
    file_name = models.CharField(blank=True, max_length=230)
    file = models.FileField(upload_to='static/uploads/')
    choice = (
        ("image", "image"),
        ("pdf", "pdf"),
        ("icons", "icons"),
        ("other", "other")

    )
    file_type = models.CharField(blank=True, max_length=30, choices=choice)
    alt_text = models.CharField(blank=True, max_length=150)
    description = models.CharField(blank=True, max_length=250)
    thumbnail = models.ImageField(upload_to='static/uploads/thumbnail/', blank=True, null=True)
    objects = DefaultManager()


    def __str__(self):
        return self.file_name


class NotificationCenter(CompanyMixins):
    CHOICES = (
        ("Email", "Email"),
        ("SMS", "SMS")
    )
    subject = models.CharField(max_length=200)
    message = models.CharField(max_length=500)
    recipient = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=20, default="Pending")
    channel = models.CharField(max_length=200, choices=CHOICES, null=True, blank=True, default="Email")

    def __str__(self):
        return self.subject


class UnitOfMeasurements(CompanyMixins):
    name = models.CharField(blank=True, max_length=150)
    unit_value = models.PositiveIntegerField(default=0)
    objects = DefaultManager()

    def __str__(self):
        return self.name


class Category(CompanyMixins):
    media_file = models.ForeignKey(MediaFiles, on_delete=models.CASCADE, null=True, related_name='category')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    objects = DefaultManager()

    def __str__(self):
        return self.name



class ItemTags(CompanyMixins):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    objects = DefaultManager()

    def __str__(self):
        return self.name



class ProductItems(CompanyMixins):
    ITEM_TYPE_CHOICES = [
        ('inventory', 'Inventory'),
        ('service', 'Service'),
        ('non_inventory', 'Non-Inventory'),
    ]
    umo = models.ForeignKey(UnitOfMeasurements, on_delete=models.CASCADE, null=True, related_name='item_umo')
    media_file = models.ForeignKey(MediaFiles, on_delete=models.CASCADE, null=True, related_name='item_file')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='items')
    tags = models.ManyToManyField(ItemTags, null=True, blank=True, related_name='item_tags')
    serial_no = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    item_type = models.CharField(max_length=100, choices=ITEM_TYPE_CHOICES, blank=True)
    tax_applied = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    barcode = models.CharField(max_length=250, blank=True)
    promo_code = models.CharField(max_length=250, blank=True)
    sku = models.CharField(max_length=250, blank=True)
    objects = DefaultManager()

    def __str__(self):
        return self.name


class ActivityLog(CompanyMixins):
    user = models.ForeignKey("accounts.Users", on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action_type = models.CharField(max_length=50, null=True, blank=True)
    module = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    objects = DefaultManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action_type} at {self.created_at}"




@receiver(post_save, sender=MediaFiles, dispatch_uid="create_or_update_thumbnail")
def create_or_update_thumbnail(sender, instance, **kwargs):
    if instance.file_type == 'image' and instance.file:
        try:
            original_image = Image.open(instance.file)
            new_size = (200, 200)
            original_image.thumbnail(new_size)
            file_format = original_image.format or "JPEG"
            thumbnail_io = BytesIO()
            original_image.save(thumbnail_io, format=file_format)
            thumbnail_content = ContentFile(thumbnail_io.getvalue())
            instance.thumbnail.save(instance.file_name, thumbnail_content, save=False)

            instance.save(update_fields=["thumbnail"])
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
