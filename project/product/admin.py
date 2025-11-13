from django.contrib import admin

from .models import MediaFiles, UnitOfMeasurements, Category, ProductItems, NotificationCenter, ActivityLog, ItemTags

# Register your models here.
admin.site.site_header = "MK Riyada Invoicing Solutions for Saudi SMEs"
admin.site.site_title = "MK Riyada Invoicing Solutions Panel"
admin.site.index_title = "Welcome to MK Riyada Invoicing Solutions Panel"


admin.site.register(MediaFiles)

@admin.register(UnitOfMeasurements)
class UnitOfMeasurementsAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['company__name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_filter = ['company__name']


@admin.register(ProductItems)
class ProductItemsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_filter = ['company__name']
    list_display = (['serial_no', 'name', 'unit_price', 'status'])



@admin.register(ItemTags)
class ItemTagsAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_filter = ['company__name']
    list_display = ['name', 'description']

admin.site.register(NotificationCenter)
admin.site.register(ActivityLog)


