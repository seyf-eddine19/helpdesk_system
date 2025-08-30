from django.contrib import admin
from .models import User, Employee


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("full_name_ar", "full_name_en", "department", "phone_number", "user")}),
    )
    list_display = ("full_name_ar", "full_name_en", "department", "phone_number", "user")
    list_filter = ("department",)
    search_fields = ("full_name_ar", "full_name_en", "phone_number", "user__username")
