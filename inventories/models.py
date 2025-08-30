from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class InkCategory(models.Model):
    name_ar = models.CharField(max_length=100, unique=True, verbose_name=_("Ink Category (Arabic)"))
    name_en = models.CharField(max_length=100, unique=True, verbose_name=_("Ink Category (English)"))

    class Meta:
        verbose_name = _("Ink Category")
        verbose_name_plural = _("Ink Categories")
        ordering = ["name_en"]

    def __str__(self):
        # Show both languages (you can customize this)
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
    category = models.ForeignKey(
        OfficeSupplyCategory,
        on_delete=models.CASCADE,
        related_name="supplies",
        verbose_name=_("Category"),
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Office Supply")
        verbose_name_plural = _("Office Supplies")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar} - {self.quantity}"
