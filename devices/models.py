from django.db import models
from employees.models import User
from django.utils.translation import gettext_lazy as _


class Condition(models.TextChoices):
    NEW = "new", _("New")
    USED = "used", _("Used")
    DAMAGED = "damaged", _("Damaged")
    LOST = "lost", _("Lost")


class Status(models.TextChoices):
    AVAILABLE = "available", _("Available")
    IN_USE = "in_use", _("In Use")
    MAINTENANCE = "maintenance", _("Under Maintenance")
    LOST = "lost", _("Lost")


# Device Type
class DeviceType(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_("Device Type (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Device Type (English)"))

    class Meta:
        verbose_name = _("Device Type")
        verbose_name_plural = _("Device Types")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar}"


# Device
class Device(models.Model):
    name_ar = models.CharField(max_length=100, verbose_name=_("Device Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Device Name (English)"))
    serial_number = models.CharField(max_length=100, unique=True, verbose_name=_("Serial Number"))
    device_type = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True, verbose_name=_("Device Type"))
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.AVAILABLE, verbose_name=_("Status"))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Added At"))

    def count_accessories(self):
        return self.accessories.count()

    class Meta:
        verbose_name = _("Device")
        verbose_name_plural = _("Devices")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar} - {self.serial_number}"


class DeviceAccessory(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="accessories", verbose_name=_("Device"))
    name_ar = models.CharField(max_length=100, verbose_name=_("Accessory Name (Arabic)"))
    name_en = models.CharField(max_length=100, verbose_name=_("Accessory Name (English)"))
    condition = models.CharField(max_length=50, choices=Condition.choices, default=Condition.NEW, verbose_name=_("Condition"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Accessory")
        verbose_name_plural = _("Accessories")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en} / {self.name_ar} ({self.device})"


# Custody
class Custody(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Employee"))
    custody_date = models.DateField(verbose_name=_("Custody Date"))
    return_date = models.DateField(null=True, blank=True, verbose_name=_("Return Date"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    def count_devices(self):
        return self.devices.count()
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
       
        for device_custody in self.devices.all():
            if self.return_date:
                device_custody.device.status = Status.AVAILABLE
            elif is_new:
                device_custody.device.status = Status.IN_USE
            device_custody.device.save()

    class Meta:
        verbose_name = _("Custody")
        verbose_name_plural = _("Custodies")
        ordering = ["-custody_date"]

    def __str__(self):
        return f"Custody {self.employee} on {self.custody_date}"


class DeviceCustody(models.Model):
    custody = models.ForeignKey(Custody, on_delete=models.CASCADE, related_name="devices")
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="custodies")
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    accessories = models.ManyToManyField("DeviceAccessory", through="AccessoryCustody", related_name="custodies", verbose_name=_("Accessories"))

    def savetest(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.custody.return_date:
            self.device.status = Status.AVAILABLE
        else:
            self.device.status = Status.IN_USE
        self.device.save()

    class Meta:
        verbose_name = _("Device Custody")
        verbose_name_plural = _("Device Custodies")
        unique_together = ("custody", "device")

    def __str__(self):
        return f"{self.device} with {self.custody.employee}"


class AccessoryCustody(models.Model):
    device_custody = models.ForeignKey(DeviceCustody, on_delete=models.CASCADE)
    accessory = models.ForeignKey(DeviceAccessory, on_delete=models.CASCADE, verbose_name=_("Accessory"))

    class Meta:
        verbose_name = _("Accessory Custody")
        verbose_name_plural = _("Accessories Custody")

    def __str__(self):
        return f"{self.accessory} for {self.device_custody}"
