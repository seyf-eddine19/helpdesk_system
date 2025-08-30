from django.contrib import admin
from .models import InkCategory, InkInventory, OfficeSupplyCategory, OfficeSupply


@admin.register(InkCategory)
class InkCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name_en", "name_ar")


@admin.register(InkInventory)
class InkInventoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "category", "quantity", "created_at", "updated_at")
    list_filter = ("category",)
    search_fields = ("name_en", "name_ar")


@admin.register(OfficeSupplyCategory)
class OfficeSupplyCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name_en", "name_ar")


@admin.register(OfficeSupply)
class OfficeSupplyAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "category", "quantity", "created_at", "updated_at")
    list_filter = ("category",)
    search_fields = ("name_en", "name_ar")
