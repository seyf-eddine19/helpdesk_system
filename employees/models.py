from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False,
        null=False
    )
    groups = models.ManyToManyField(
        Group,
        related_name="user_set",
        related_query_name="user",
        verbose_name=_("Type")
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username


class Employee(models.Model):
    """Employee profile linked to User."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    full_name_ar = models.CharField(max_length=150, verbose_name=_("Full Name (Arabic)"))
    full_name_en = models.CharField(max_length=150, verbose_name=_("Full Name (English)"))
    birth_date = models.DateField(blank=True, null=True, verbose_name=_("Birth Date"))
    id_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("ID / Iqama Number"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    job_title = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Job Title"))
    job_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Job Number"))
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Department"))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Phone Number"))

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")

    def __str__(self):
        return self.full_name_en or self.user.username

