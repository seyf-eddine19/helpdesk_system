from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import models

from .forms import EmployeeCreationForm, EmployeeUpdateForm, ProfileUpdateForm
from .mixins import PermissionMixin
from .models import Employee, User
from tickets.models import Ticket
from devices.models import Device, Custody
from inventories.models import InkInventory, OfficeSupply


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)

def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

# Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        user_groups = user.groups.values_list("name", flat=True)
        is_manager_or_it = any(g in ["Manager", "IT Employee"] for g in user_groups)

        if is_manager_or_it or user.is_superuser:
            # Employees
            context["employees_summary"] = {
                "total": Employee.objects.count(),
                "active": Employee.objects.filter(user__is_active=True).count(),
                "inactive": Employee.objects.filter(user__is_active=False).count(),
                "by_department": Employee.objects.values("department").annotate(count=models.Count("id")),
                "by_job_title": Employee.objects.values("job_title").annotate(count=models.Count("id")),
                "departments": Employee.objects.values("department").distinct().count(),
                "job_titles": Employee.objects.values("job_title").distinct().count(),
            }

            # Tickets
            context["tickets_summary"] = {
                "total": Ticket.objects.count(),
                "new": Ticket.objects.filter(status="NEW").count(),
                "in_progress": Ticket.objects.filter(status="IN_PROGRESS").count(),
                "resolved": Ticket.objects.filter(status="RESOLVED").count(),
                "rejected": Ticket.objects.filter(status="REJECTED").count(),
            }

            # Devices
            context["devices_summary"] = {
                "total": Device.objects.count(),
                "available": Device.objects.filter(status="available").count(),
                "in_use": Device.objects.filter(status="in_use").count(),
                "maintenance": Device.objects.filter(status="maintenance").count(),
                "lost": Device.objects.filter(status="lost").count(),
            }

            # Custodies
            context["custodies_summary"] = {
                "total": Custody.objects.count(),
                "active": Custody.objects.filter(return_date__isnull=True).count(),
                "inactive": Custody.objects.filter(return_date__isnull=False).count(),
                "my_custodies": 0,
            }

            # Inventories
            context["inventories_summary"] = {
                "inks": InkInventory.objects.count(),
                "office_supplies": OfficeSupply.objects.count(),
            }

            context["recent_tickets"] = Ticket.objects.order_by("-created_at")[:5]
            context["recent_custodies"] = (
                Custody.objects
                .select_related("employee")
                .prefetch_related("devices__device")
                .order_by("-id")[:5]
            )
        else:
            # Restricted (Employee/Technician)
            context["tickets_summary"] = {
                "total": Ticket.objects.filter(employee=user).count(),
                "new": Ticket.objects.filter(employee=user, status="NEW").count(),
                "in_progress": Ticket.objects.filter(employee=user, status="IN_PROGRESS").count(),
                "resolved": Ticket.objects.filter(employee=user, status="RESOLVED").count(),
                "rejected": Ticket.objects.filter(employee=user, status="REJECTED").count(),
            }
            context["custodies_summary"] = {
                "my_custodies": Custody.objects.filter(employee=user.employee_profile.pk).count() if hasattr(user, "employee") else 0,
            }
            context["recent_tickets"] = Ticket.objects.filter(employee=user.employee_profile.pk).order_by("-created_at")[:5]
            context["recent_custodies"] = (
                Custody.objects
                .filter(employee=user.employee_profile.pk)
                .select_related("employee")
                .prefetch_related("devices__device")
                .order_by("-id")[:5]
            )

        return context

User = get_user_model()    
class CPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    html_email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(self.request, _("This email does not exist in our records."))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_email_context(self, user):
        """إضافة بيانات إضافية للقالب"""
        context = super().get_email_context(user)
        context["full_name_en"] = getattr(user, "full_name_en", "")
        context["department"] = getattr(user, "department", "")
        context["job_title"] = getattr(user, "job_title", "")
        return context


# Profile update (only self)
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("dashboard")

    def get_object(self, queryset=None):
        return self.request.user


# Employee CRUD (restricted)
class EmployeeListView(PermissionMixin, ListView):
    model = Employee
    template_name = "employees/list.html"
    context_object_name = "employees"
    permission_required = "employees.view_employee"


class EmployeeDetailView(PermissionMixin, DetailView):
    model = User
    template_name = "employees/detail.html"
    context_object_name = "employee"
    permission_required = "employees.view_employee"


class EmployeeCreateView(PermissionMixin, CreateView):
    model = User
    form_class = EmployeeCreationForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("employee_list")
    permission_required = "employees.add_employee"


class EmployeeUpdateView(PermissionMixin, UpdateView):
    model = User
    form_class = EmployeeUpdateForm
    template_name = "employees/form.html"
    success_url = reverse_lazy("employee_list")
    permission_required = "employees.change_employee"


class EmployeeDeleteView(PermissionMixin, DeleteView):
    model = User
    template_name = "employees/delete.html"
    success_url = reverse_lazy("employee_list")
    permission_required = "employees.delete_employee"
