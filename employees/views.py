from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Employee, User
from .forms import EmployeeCreationForm, EmployeeUpdateForm, ProfileUpdateForm
from .mixins import PermissionMixin
from django.shortcuts import render


def error_403(request, exception=None):
    return render(request, "errors/403.html", status=403)

def error_404(request, exception=None):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)


# -----------------------------
# Dashboard
# -----------------------------
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"


# -----------------------------
# Profile update (only self)
# -----------------------------
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "employees/profile_update.html"
    success_url = reverse_lazy("dashboard")

    def get_object(self, queryset=None):
        return self.request.user


# -----------------------------
# Employee CRUD (restricted)
# -----------------------------
class EmployeeListView(PermissionMixin, ListView):
    model = User
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
