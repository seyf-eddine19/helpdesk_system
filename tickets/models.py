from django.db import models
from django.utils.translation import gettext_lazy as _
from employees.models import User


class TicketStatus(models.TextChoices):
    NEW = "NEW", _("New")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    RESOLVED = "RESOLVED", _("Resolved")
    REJECTED = "REJECTED", _("Rejected")


class Priority(models.TextChoices):
    NORMAL = "NORMAL", _("Normal")
    URGENT = "URGENT", _("Urgent")
    HIGH = "HIGH", _("High")


class RequestType(models.Model):
    name_ar = models.CharField(max_length=120, unique=True, verbose_name=_("Type Name (Arabic)"))
    name_en = models.CharField(max_length=120, unique=True, verbose_name=_("Type Name(English)"))

    class Meta:
        verbose_name = _("Request Type")
        verbose_name_plural = _("Request Types")

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class Ticket(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    details = models.TextField(verbose_name=_("Details"))
    request_type = models.ForeignKey(RequestType, on_delete=models.PROTECT, verbose_name=_("Type"))
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets", verbose_name=_("Employee"))
    technician = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets", verbose_name=_("Technician"))
    status = models.CharField(max_length=20, choices=TicketStatus.choices, default=TicketStatus.NEW, verbose_name=_("Status"))
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL, verbose_name=_("Priority"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    technician_notes = models.TextField(blank=True, verbose_name=_("Technician Notes"))

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} - {self.title}"
