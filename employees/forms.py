from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Employee


class EmployeeCreationForm(UserCreationForm):
    """Form for creating a User and Employee profile together."""
    full_name_ar = forms.CharField(max_length=150, required=True, label=_("Full Name (Arabic)"))
    full_name_en = forms.CharField(max_length=150, required=True, label=_("Full Name (English)"))
    department = forms.CharField(max_length=100, required=False, label=_("Department"))
    phone_number = forms.CharField(max_length=20, required=False, label=_("Phone Number"))

    # 🔥 force single group select
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label=_("Type"),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username", "email", "password1", "password2",
            "full_name_ar", "full_name_en", "department", "phone_number",
            "groups", "is_active", "is_superuser",
        ]
        widgets = {
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "username": _("Username"),
            "email": _("Email"),
            "groups": _("Type"),
            "is_active": _("Active"),
            "is_superuser": _("Superuser"),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # keep only one group
            if self.cleaned_data.get("groups"):
                user.groups.set([self.cleaned_data["groups"]])
            Employee.objects.create(
                user=user,
                full_name_ar=self.cleaned_data["full_name_ar"],
                full_name_en=self.cleaned_data["full_name_en"],
                department=self.cleaned_data.get("department"),
                phone_number=self.cleaned_data.get("phone_number"),
            )
        return user


class EmployeeUpdateForm(UserChangeForm):
    """Form for updating User + Employee together."""
    full_name_ar = forms.CharField(max_length=150, required=True, label=_("Full Name (Arabic)"))
    full_name_en = forms.CharField(max_length=150, required=True, label=_("Full Name (English)"))
    department = forms.CharField(max_length=100, required=False, label=_("Department"))
    phone_number = forms.CharField(max_length=20, required=False, label=_("Phone Number"))

    # 🔥 force single group select
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label=_("Type"),
    )

    password = None  # hide password field

    class Meta:
        model = User
        fields = [
            "username", "email", "groups",
            "is_active", "is_superuser"
        ]
        widgets = {
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "username": _("Username"),
            "email": _("Email"),
            "is_active": _("Active"),
            "is_superuser": _("Superuser"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, "employee_profile"):
            self.fields["full_name_ar"].initial = self.instance.employee_profile.full_name_ar
            self.fields["full_name_en"].initial = self.instance.employee_profile.full_name_en
            self.fields["department"].initial = self.instance.employee_profile.department
            self.fields["phone_number"].initial = self.instance.employee_profile.phone_number

        print(self.instance.pk)
        if self.instance.pk:
            user_group = self.instance.groups.all().first()
            print(self.instance.groups.all(), user_group)
            if user_group:
                self.initial['groups'] = [user_group.pk] 
            else:
                self.initial["groups"] = None


    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # keep only one group
            if self.cleaned_data.get("groups"):
                user.groups.set([self.cleaned_data["groups"]])
            else:
                user.groups.clear()

            emp, created = Employee.objects.get_or_create(user=user)
            emp.full_name_ar = self.cleaned_data["full_name_ar"]
            emp.full_name_en = self.cleaned_data["full_name_en"]
            emp.department = self.cleaned_data.get("department")
            emp.phone_number = self.cleaned_data.get("phone_number")
            emp.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    full_name_ar = forms.CharField(max_length=150, required=True, label=_("Full Name (Arabic)"))
    full_name_en = forms.CharField(max_length=150, required=True, label=_("Full Name (English)"))
    department = forms.CharField(
        max_length=100,
        required=False,
        label=_("Department"),
        widget=forms.TextInput(attrs={"readonly": "readonly"})
    )
    phone_number = forms.CharField(max_length=20, required=False, label=_("Phone Number"))

    class Meta:
        model = User
        fields = ["username", "email"]
        labels = {
            "username": _("Username"),
            "email": _("Email"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        employee = getattr(self.instance, "employee_profile", None)
        if employee:
            self.fields["full_name_ar"].initial = employee.full_name_ar
            self.fields["full_name_en"].initial = employee.full_name_en
            self.fields["department"].initial = employee.department
            self.fields["phone_number"].initial = employee.phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            employee, created = Employee.objects.get_or_create(user=user)
            employee.full_name_ar = self.cleaned_data.get("full_name_ar", employee.full_name_ar)
            employee.full_name_en = self.cleaned_data.get("full_name_en", employee.full_name_en)
            employee.department = self.cleaned_data.get("department", employee.department)
            employee.phone_number = self.cleaned_data.get("phone_number", employee.phone_number)
            employee.save()
        return user
