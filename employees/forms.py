from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.apps import apps
from .models import User, Employee


class PermissionField(forms.ModelMultipleChoiceField):
    """Display permissions in Arabic/English and exclude Django built-in apps."""
    PERMISSION_TRANSLATIONS = {
        "add": _("Add"),
        "change": _("Edit"),
        "delete": _("Delete"),
        "view": _("View"),
    }
    EXCLUDE_APPS = ["auth", "contenttypes", "sessions", "admin"]

    def __init__(self, *args, app_label=None, **kwargs):
        kwargs['widget'] = forms.CheckboxSelectMultiple()
        queryset = Permission.objects.exclude(content_type__app_label__in=self.EXCLUDE_APPS)
        if app_label:
            queryset = queryset.filter(content_type__app_label=app_label)
        kwargs['queryset'] = queryset
        super().__init__(*args, **kwargs)

    def label_from_instance(self, permission):
        app_label = permission.content_type.app_label
        model_name = permission.content_type.model
        action = permission.codename.split('_')[0]

        action_label = self.PERMISSION_TRANSLATIONS.get(action)
        model_class = apps.get_model(app_label, model_name)
        model_label = getattr(model_class._meta, "verbose_name_plural", model_name)

        return f"{action_label} {model_label}" if action_label else permission.name


class EmployeeBaseForm(forms.ModelForm):
    """Base form for handling both User and Employee fields."""
    full_name_ar = forms.CharField(max_length=150, required=True, label=_("Full Name (Arabic)"))
    full_name_en = forms.CharField(max_length=150, required=True, label=_("Full Name (English)"))
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label=_("Birth Date"))
    id_number = forms.CharField(max_length=50, required=False, label=_("ID / Iqama Number"))
    address = forms.CharField(widget=forms.Textarea, required=False, label=_("Address"))
    job_title = forms.CharField(max_length=100, required=False, label=_("Job Title"))
    job_number = forms.CharField(max_length=50, required=False, label=_("Job Number"))
    department = forms.CharField(max_length=100, required=False, label=_("Department"))
    phone_number = forms.CharField(max_length=20, required=False, label=_("Phone Number"))

    groups = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label=_("Type"))
    user_permissions = PermissionField(required=False, label=_("User Permissions"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and hasattr(self.instance, "employee_profile"):
            emp = self.instance.employee_profile
            for field in ["full_name_ar", "full_name_en", "birth_date", "id_number",
                          "address", "job_title", "job_number", "department", "phone_number"]:
                self.fields[field].initial = getattr(emp, field)
            self.fields["user_permissions"].initial = self.instance.user_permissions.all()
            user_group = self.instance.groups.first()
            self.initial['groups'] = user_group.pk if user_group else None

    def save_employee(self, user):
        emp, _ = Employee.objects.get_or_create(user=user)
        for field in ["full_name_ar", "full_name_en", "birth_date", "id_number",
                      "address", "job_title", "job_number", "department", "phone_number"]:
            setattr(emp, field, self.cleaned_data.get(field))
        emp.save()


class EmployeeCreationForm(EmployeeBaseForm, UserCreationForm):
    """Form for creating a User and Employee profile together."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username", "email", "password1", "password2",
            "full_name_ar", "full_name_en", "birth_date",
            "id_number", "address", "job_title", "job_number", "department", "phone_number",
            "groups", "user_permissions", "is_active", "is_superuser",
        ]
        widgets = {
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Set single group
            if self.cleaned_data.get("groups"):
                user.groups.set([self.cleaned_data["groups"]])
            else:
                user.groups.clear()
            # Save employee fields
            self.save_employee(user)
            # Save selected permissions
            user.user_permissions.set(self.cleaned_data.get("user_permissions"))
        return user


class EmployeeUpdateForm(EmployeeBaseForm, UserChangeForm):
    """Form for updating User + Employee together."""
    password = None  # hide password field

    class Meta(UserChangeForm.Meta):
        model = User
        fields = [
            "username", "email",
            "full_name_ar", "full_name_en", "birth_date",
            "id_number", "address", "job_title", "job_number", "department", "phone_number",
            "groups", "user_permissions", "is_active", "is_superuser",
        ]
        widgets = {
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_superuser": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Keep only one group
            if self.cleaned_data.get("groups"):
                user.groups.set([self.cleaned_data["groups"]])
            else:
                user.groups.clear()
            # Save employee fields
            self.save_employee(user)
            # Save selected permissions
            user.user_permissions.set(self.cleaned_data.get("user_permissions"))
        return user


class ProfileUpdateForm(forms.ModelForm):
    full_name_ar = forms.CharField(max_length=150, required=True, label=_("Full Name (Arabic)"))
    full_name_en = forms.CharField(max_length=150, required=True, label=_("Full Name (English)"))
    birth_date = forms.DateField(required=False, label=_("Birth Date"), widget=forms.DateInput(attrs={'type': 'date'}))
    id_number = forms.CharField(max_length=50, required=False, label=_("ID / Iqama Number"))
    address = forms.CharField(widget=forms.Textarea, required=False, label=_("Address"))
    job_title = forms.CharField(max_length=100, required=False, label=_("Job Title"), widget=forms.TextInput(attrs={"readonly": "readonly"}))
    job_number = forms.CharField(max_length=50, required=False, label=_("Job Number"), widget=forms.TextInput(attrs={"readonly": "readonly"}))
    department = forms.CharField(max_length=100, required=False, label=_("Department"), widget=forms.TextInput(attrs={"readonly": "readonly"}))
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
            self.fields["birth_date"].initial = employee.birth_date
            self.fields["id_number"].initial = employee.id_number
            self.fields["address"].initial = employee.address
            self.fields["job_title"].initial = employee.job_title
            self.fields["job_number"].initial = employee.job_number
            self.fields["department"].initial = employee.department
            self.fields["phone_number"].initial = employee.phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            employee, created = Employee.objects.get_or_create(user=user)
            employee.full_name_ar = self.cleaned_data.get("full_name_ar", employee.full_name_ar)
            employee.full_name_en = self.cleaned_data.get("full_name_en", employee.full_name_en)
            employee.birth_date = self.cleaned_data.get("birth_date", employee.birth_date)
            employee.id_number = self.cleaned_data.get("id_number", employee.id_number)
            employee.address = self.cleaned_data.get("address", employee.address)
            # employee.job_title = self.cleaned_data.get("job_title", employee.job_title)
            # employee.job_number = self.cleaned_data.get("job_number", employee.job_number)
            # employee.department = self.cleaned_data.get("department", employee.department)
            employee.phone_number = self.cleaned_data.get("phone_number", employee.phone_number)
            employee.save()
        return user
