from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class InkCategory(models.Model):
    name_ar = models.CharField(max_length=100, unique=True, verbose_name=_("Ink Category (Arabic)"))
    name_en = models.CharField(max_length=100, unique=True, verbose_name=_("Ink Category (English)"))

    class Meta:
        verbose_name = _("Ink Category")
        verbose_name_plural = _("Ink Categories")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class InkInventory(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_("Ink Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Ink Name (English)"))
    category = models.ForeignKey(
        InkCategory,
        on_delete=models.CASCADE,
        related_name="inks",
        verbose_name=_("Category"),
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Ink")
        verbose_name_plural = _("Inks")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar} - {self.quantity}"


class InkRequest(models.Model):
    """تسجيل كل عملية خصم/طلب للحبر"""
    ink = models.ForeignKey(InkInventory, on_delete=models.CASCADE, related_name="requests", verbose_name=_("Ink"))
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Requested By"))
    quantity_used = models.PositiveIntegerField(verbose_name=_("Quantity Used"))
    reason = models.TextField(blank=True, null=True, verbose_name=_("Reason / Purpose"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Requested At"))

    class Meta:
        verbose_name = _("Ink Request")
        verbose_name_plural = _("Ink Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ink.name_en} - {self.quantity_used} by {self.requested_by}"

    def save(self, *args, **kwargs):
        """عند إنشاء طلب جديد يتم خصم الكمية مباشرة من المخزون"""
        if not self.pk:  # فقط عند الإنشاء الجديد
            if self.ink.quantity < self.quantity_used:
                raise ValueError(_("Not enough ink in stock"))
            self.ink.quantity -= self.quantity_used
            self.ink.save()
        super().save(*args, **kwargs)


class OfficeSupplyCategory(models.Model):
    name_ar = models.CharField(max_length=100, unique=True, verbose_name=_("Supply Category (Arabic)"))
    name_en = models.CharField(max_length=100, unique=True, verbose_name=_("Supply Category (English)"))

    class Meta:
        verbose_name = _("Supply Category")
        verbose_name_plural = _("Supply Categories")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


class OfficeSupply(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_("Supply Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Supply Name (English)"))
    category = models.ForeignKey(OfficeSupplyCategory, on_delete=models.CASCADE, related_name="supplies", verbose_name=_("Category"),)
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Office Supply")
        verbose_name_plural = _("Office Supplies")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar} - {self.quantity}"
