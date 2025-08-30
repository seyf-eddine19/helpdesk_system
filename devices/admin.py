from django.contrib import admin
from .models import (
    DeviceType, Device, DeviceAccessory,
    Custody, DeviceCustody, AccessoryCustody
)


# -----------------------------
# Device Type
# -----------------------------
@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar")
    search_fields = ("name_en", "name_ar")


# -----------------------------
# Device Accessory
# -----------------------------
@admin.register(DeviceAccessory)
class DeviceAccessoryAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ar", "model", "condition")
    list_filter = ("condition",)
    search_fields = ("name_en", "name_ar", "model")


# -----------------------------
# Device
# -----------------------------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("serial_number", "status", "added_at")
    list_filter = ("status",)
    search_fields = ("serial_number",)
    # filter_horizontal = ("accessories",)
    date_hierarchy = "added_at"


# -----------------------------
# Accessory Custody (Inline)
# -----------------------------
class AccessoryCustodyInline(admin.TabularInline):
    model = AccessoryCustody
    extra = 1


# -----------------------------
# Device Custody (Inline + Admin)
# -----------------------------
class DeviceCustodyInline(admin.TabularInline):
    model = DeviceCustody
    extra = 1


@admin.register(DeviceCustody)
class DeviceCustodyAdmin(admin.ModelAdmin):
    list_display = ("device", "custody")
    search_fields = ("device__serial_number", "custody__employee__username")
    inlines = [AccessoryCustodyInline]


# -----------------------------
# Custody
# -----------------------------
@admin.register(Custody)
class CustodyAdmin(admin.ModelAdmin):
    list_display = ("employee", "custody_date", "return_date")
    list_filter = ("custody_date", "return_date")
    search_fields = ("employee__username",)
    date_hierarchy = "custody_date"
    inlines = [DeviceCustodyInline]


# -----------------------------
# Accessory Custody
# -----------------------------
@admin.register(AccessoryCustody)
class AccessoryCustodyAdmin(admin.ModelAdmin):
    list_display = ("accessory", "device_custody")
    list_filter = ("accessory__condition",)
    search_fields = ("accessory__name", "device_custody__device__serial_number")
