from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from employees.mixins import PermissionMixin
from employees.models import User
from .models import Ticket, RequestType


from django.db import IntegrityError, DatabaseError

# Request Types View
@login_required
@permission_required("tickets.view_requesttype", raise_exception=True)
def request_type_manage(request):
    edit_id = request.GET.get("edit")
    delete_id = request.GET.get("delete")

    # ---------------- Delete ----------------
    if delete_id:
        if not request.user.has_perm("tickets.delete_requesttype") and not request.user.is_superuser:
            messages.error(request, _("You do not have permission to delete a request type"))
            return redirect("requesttype_manage")

        obj = get_object_or_404(RequestType, pk=delete_id)
        try:
            obj.delete()
            messages.success(request, _("Request type deleted successfully"))
        except Exception:
            messages.error(request, _("An unexpected error occurred while deleting"))
        return redirect("requesttype_manage")

    # ---------------- Add / Edit ----------------
    if request.method == "POST":
        name_ar = request.POST.get("name_ar", "").strip()
        name_en = request.POST.get("name_en", "").strip()
        if not name_en or not name_ar:
            messages.error(request, _("Both English and Arabic names are required."))
            return redirect("supplycategory_manage")

        try:
            if edit_id:  # Edit
                if not request.user.has_perm("tickets.change_requesttype") and not request.user.is_superuser:
                    messages.error(request, _("You do not have permission to edit a request type"))
                    return redirect("requesttype_manage")

                obj = get_object_or_404(RequestType, pk=edit_id)

                # Prevent duplicate name_en or name_ar
                if RequestType.objects.exclude(pk=obj.pk).filter(name_en=name_en).exists():
                    messages.error(request, _("A request type with this English name already exists"))
                    return redirect("requesttype_manage")
                if RequestType.objects.exclude(pk=obj.pk).filter(name_ar=name_ar).exists():
                    messages.error(request, _("A request type with this Arabic name already exists"))
                    return redirect("requesttype_manage")

                obj.name_ar = name_ar
                obj.name_en = name_en
                obj.save()
                messages.success(request, _("Request type updated successfully"))

            else:  # Add
                if not request.user.has_perm("tickets.add_requesttype") and not request.user.is_superuser:
                    messages.error(request, _("You do not have permission to add a request type"))
                    return redirect("requesttype_manage")

                # Prevent duplicate before creating
                if RequestType.objects.filter(name_en=name_en).exists():
                    messages.error(request, _("A request type with this English name already exists"))
                    return redirect("requesttype_manage")
                if RequestType.objects.filter(name_ar=name_ar).exists():
                    messages.error(request, _("A request type with this Arabic name already exists"))
                    return redirect("requesttype_manage")

                RequestType.objects.create(name_ar=name_ar, name_en=name_en)
                messages.success(request, _("Request type added successfully"))

        except IntegrityError:
            messages.error(request, _("A database integrity error occurred. Please check your data."))
        except DatabaseError:
            messages.error(request, _("A database error occurred. Please try again later."))
        except Exception:
            messages.error(request, _("An unexpected error occurred. Please try again."))

        return redirect("requesttype_manage")

    # ---------------- Render ----------------
    request_types = RequestType.objects.all()
    current_edit = None
    if edit_id:
        current_edit = get_object_or_404(RequestType, pk=edit_id)

    return render(request, "tickets/requesttype_manage.html", {
        "request_types": request_types,
        "current_edit": current_edit,
    })


class TicketListView(PermissionMixin, ListView):
    model = Ticket
    template_name = "tickets/list.html"
    context_object_name = "tickets"
    paginate_by = 10
    permission_required = "tickets.view_ticket"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("employee", "technician", "request_type").order_by("-created_at")
        if self.request.user.groups.filter(name="Employee").exists() and not self.request.user.is_superuser:
            queryset = queryset.filter(employee=self.request.user)
        elif self.request.user.groups.filter(name="Technician").exists() and not self.request.user.is_superuser:
            queryset = queryset.filter(technician=self.request.user)

        # Filters
        type_filter = self.request.GET.get("request_type")
        status_filter = self.request.GET.get("status")
        priority_filter = self.request.GET.get("priority")
        search_query = self.request.GET.get("q")

        if type_filter:
            queryset = queryset.filter(request_type__id=type_filter)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["request_types"] = RequestType.objects.all()
        context["selected_request_type"] = self.request.GET.get("request_type")
        context["selected_status"] = self.request.GET.get("status")
        context["selected_priority"] = self.request.GET.get("priority")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class TicketDetailView(PermissionMixin, DetailView):
    model = Ticket
    template_name = "tickets/detail.html"
    context_object_name = "ticket"
    permission_required = "tickets.view_ticket"


class TicketCreateView(PermissionMixin, CreateView):
    model = Ticket
    fields = ["employee", "title", "details", "request_type", "priority", "technician",]
    template_name = "tickets/form.html"
    success_url = reverse_lazy("ticket_list")
    permission_required = "tickets.add_ticket"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.groups.filter(name__in=["IT Employee", "Manager"]).exists() or self.request.user.is_superuser:
            technician_field = self.model._meta.get_field("technician").formfield()
            technician_field.queryset = User.objects.filter(groups__name__in=["IT Employee", "Technician"])
            form.fields["technician"] = technician_field
            form.fields["employee"] = self.model._meta.get_field("employee").formfield()
        else:
            form.fields.pop("technician", None)
            form.fields.pop("employee", None)
        return form
    
    def form_valid(self, form):
        if self.request.user.groups.filter(name="Employee").exists():
            form.instance.employee = self.request.user
        messages.success(self.request, _("Ticket created successfully"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Failed to create ticket"))
        return super().form_invalid(form)


class TicketUpdateView(PermissionMixin, UpdateView):
    model = Ticket
    fields = ["employee", "title", "details", "request_type", "priority", "status", "technician", "technician_notes"]
    template_name = "tickets/form.html"
    success_url = reverse_lazy("ticket_list")
    permission_required = "tickets.change_ticket"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field_name in ["employee", "title", "details", "request_type", "priority"]:
            if field_name in form.fields:
                form.fields[field_name].disabled = True

        if self.request.user.groups.filter(name__in=["IT Employee", "Manager"]).exists() or self.request.user.is_superuser:
            technician_field = self.model._meta.get_field("technician").formfield()
            technician_field.queryset = User.objects.filter(groups__name__in=["IT Employee", "Technician"]) 
            form.fields["technician"] = technician_field
        else:
            form.fields.pop("technician", None)

        return form

    def form_valid(self, form):
        messages.success(self.request, _("Ticket updated successfully"))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _("Failed to update ticket"))
        return super().form_invalid(form)


class TicketDeleteView(PermissionMixin, DeleteView):
    model = Ticket
    template_name = "tickets/delete.html"
    success_url = reverse_lazy("ticket_list")
    permission_required = "tickets.delete_ticket"

    def delete(self, request, *args, **kwargs):
        try:
            messages.success(self.request, _("Ticket deleted successfully"))
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(self.request, _("Failed to delete ticket: %s") % str(e))
            return redirect(self.success_url)

