from django.contrib import admin
from .models import RequestType, Ticket


@admin.register(RequestType)
class RequestTypeAdmin(admin.ModelAdmin):
    search_fields = ("name_ar", "name_en")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "employee", "technician", "status",
        "priority", "request_type", "created_at", "updated_at"
    )
    list_filter = ("status", "priority", "request_type", "created_at")
    search_fields = ("title", "details", "employee__full_name_ar", "technician__full_name_ar")
    date_hierarchy = "created_at"
