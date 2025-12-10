from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import InkCategory, InkInventory, InkRequest, OfficeSupplyCategory, OfficeSupply
from .forms import InkInventoryForm, InkRequestForm, OfficeSupplyForm

from employees.mixins import PermissionMixin

from django.db import IntegrityError, DatabaseError
from django.db.models import Q

# -------------------------------
# Ink Category Manager
# -------------------------------
@login_required
@permission_required("inventories.view_inkcategory", raise_exception=True)
def inkcategory_manage(request):
    edit_id = request.GET.get("edit")
    delete_id = request.GET.get("delete")

    # --- Delete ---
    if delete_id:
        if not request.user.has_perm("inventories.delete_inkcategory") and not request.user.is_superuser:
            messages.error(request, _("You do not have permission to delete an ink category"))
            return redirect("inkcategory_manage")

        obj = get_object_or_404(InkCategory, pk=delete_id)
        try:
            obj.delete()
            messages.success(request, _("Ink category deleted successfully"))
        except Exception:
            messages.error(request, _("An unexpected error occurred while deleting"))
        return redirect("inkcategory_manage")

    # --- Add / Edit ---
    if request.method == "POST":
        name_ar = request.POST.get("name_ar", "").strip()
        name_en = request.POST.get("name_en", "").strip()
        if not name_en or not name_ar:
            messages.error(request, _("Both English and Arabic names are required."))
            return redirect("supplycategory_manage")

        try:
            if edit_id:  # Edit
                if not request.user.has_perm("inventories.change_inkcategory") and not request.user.is_superuser:
                    messages.error(request, _("You do not have permission to edit an ink category"))
                    return redirect("inkcategory_manage")

                obj = get_object_or_404(InkCategory, pk=edit_id)

                # Duplicate checks
                if InkCategory.objects.exclude(pk=obj.pk).filter(name_en=name_en).exists():
                    messages.error(request, _("An ink category with this English name already exists"))
                    return redirect("inkcategory_manage")
                if InkCategory.objects.exclude(pk=obj.pk).filter(name_ar=name_ar).exists():
                    messages.error(request, _("An ink category with this Arabic name already exists"))
                    return redirect("inkcategory_manage")

                obj.name_ar = name_ar
                obj.name_en = name_en
                obj.save()
                messages.success(request, _("Ink category updated successfully"))

            else:  # Add
                if not request.user.has_perm("inventories.add_inkcategory") and not request.user.is_superuser:
                    messages.error(request, _("You do not have permission to add an ink category"))
                    return redirect("inkcategory_manage")

                # Duplicate checks
                if InkCategory.objects.filter(name_en=name_en).exists():
                    messages.error(request, _("An ink category with this English name already exists"))
                    return redirect("inkcategory_manage")
                if InkCategory.objects.filter(name_ar=name_ar).exists():
                    messages.error(request, _("An ink category with this Arabic name already exists"))
                    return redirect("inkcategory_manage")

                InkCategory.objects.create(name_ar=name_ar, name_en=name_en)
                messages.success(request, _("Ink category added successfully"))

        except IntegrityError:
            messages.error(request, _("A database integrity error occurred. Please check your data."))
        except DatabaseError:
            messages.error(request, _("A database error occurred. Please try again later."))
        except Exception:
            messages.error(request, _("An unexpected error occurred. Please try again."))

        return redirect("inkcategory_manage")

    # --- Render ---
    categories = InkCategory.objects.all()
    current_edit = None
    if edit_id:
        current_edit = get_object_or_404(InkCategory, pk=edit_id)

    return render(request, "inventory/inkcategory_manage.html", {
        "categories": categories,
        "current_edit": current_edit,
    })


# -------------------------------
# Office Supply Category Manager
# -------------------------------
@login_required
@permission_required("inventories.view_officesupplycategory", raise_exception=True)
def supplycategory_manage(request):
    edit_id = request.GET.get("edit")
    delete_id = request.GET.get("delete")

    # --- Delete ---
    if delete_id:
        if not request.user.has_perm("inventories.delete_officesupplycategory") and not request.user.is_superuser:
            messages.error(request, _("You do not have permission to delete a supply category"))
            return redirect("supplycategory_manage")

        obj = get_object_or_404(OfficeSupplyCategory, pk=delete_id)
        try:
            obj.delete()
            messages.success(request, _("Supply category deleted successfully"))
        except Exception:
            messages.error(request, _("An unexpected error occurred while deleting"))
        return redirect("supplycategory_manage")

    # --- Add / Edit ---
    if request.method == "POST":
        name_ar = request.POST.get("name_ar", "").strip()
        name_en = request.POST.get("name_en", "").strip()

        if not name_en or not name_ar:
            messages.error(request, _("Both English and Arabic names are required."))
            return redirect("supplycategory_manage")

        try:
            if edit_id:  # Edit
                if not request.user.has_perm("inventories.change_officesupplycategory") and not request.user.is_superuser:
                    messages.error(request, _("You do not have permission to edit a supply category"))
                    return redirect("supplycategory_manage")

                obj = get_object_or_404(OfficeSupplyCategory, pk=edit_id)

                # Duplicate checks
                if OfficeSupplyCategory.objects.exclude(pk=obj.pk).filter(name_en=name_en).exists():
                    messages.error(request, _("A supply category with this English name already exists"))
                    return redirect("supplycategory_manage")
                if OfficeSupplyCategory.objects.exclude(pk=obj.pk).filter(name_ar=name_ar).exists():
                    messages.error(request, _("A supply category with this Arabic name already exists"))
                    return redirect("supplycategory_manage")

                obj.name_ar = name_ar
                obj.name_en = name_en
                obj.save()
                messages.success(request, _("Supply category updated successfully"))

            else:  # Add
                if not request.user.has_perm("inventories.add_officesupplycategory") and not request.user.is_superuser:
                    messages.error(request, _("You do not have permission to add a supply category"))
                    return redirect("supplycategory_manage")

                # Duplicate checks
                if OfficeSupplyCategory.objects.filter(name_en=name_en).exists():
                    messages.error(request, _("A supply category with this English name already exists"))
                    return redirect("supplycategory_manage")
                if OfficeSupplyCategory.objects.filter(name_ar=name_ar).exists():
                    messages.error(request, _("A supply category with this Arabic name already exists"))
                    return redirect("supplycategory_manage")

                OfficeSupplyCategory.objects.create(name_ar=name_ar, name_en=name_en)
                messages.success(request, _("Supply category added successfully"))

        except IntegrityError:
            messages.error(request, _("A database integrity error occurred. Please check your data."))
        except DatabaseError:
            messages.error(request, _("A database error occurred. Please try again later."))
        except Exception:
            messages.error(request, _("An unexpected error occurred. Please try again."))

        return redirect("supplycategory_manage")

    # --- Render ---
    categories = OfficeSupplyCategory.objects.all()
    current_edit = None
    if edit_id:
        current_edit = get_object_or_404(OfficeSupplyCategory, pk=edit_id)

    return render(request, "inventory/supplycategory_manage.html", {
        "categories": categories,
        "current_edit": current_edit,
    })


# --- Inks ---
class InkCategoryDeleteView(PermissionMixin, DeleteView):
    model = InkCategory
    template_name = "inventory/delete.html"
    success_url = reverse_lazy("inkcategory_manage")
    permission_required = "inventories.delete_inkcategory"


class InkInventoryListView(PermissionMixin, ListView):
    model = InkInventory
    template_name = "inventory/inkinvent_list.html"
    context_object_name = "inks"
    permission_required = "inventories.view_inkinventory"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category").order_by("-updated_at")
        category_id = self.request.GET.get("category", "").strip()

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(name_en__icontains=search_query) |
                Q(name_ar__icontains=search_query)
            )
        if category_id.isdigit():
            queryset = queryset.filter(category_id=category_id)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = InkCategory.objects.all()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_category"] = self.request.GET.get("category", "").strip()
        return context


class InkInventoryCreateView(PermissionMixin, CreateView):
    model = InkInventory
    form_class = InkInventoryForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("inkinvent_list")
    permission_required = "inventories.add_inkinventory"


class InkInventoryUpdateView(PermissionMixin, UpdateView):
    model = InkInventory
    form_class = InkInventoryForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("inkinvent_list")
    permission_required = "inventories.change_inkinventory"


class InkInventoryDeleteView(PermissionMixin, DeleteView):
    model = InkInventory
    template_name = "inventory/delete.html"
    success_url = reverse_lazy("inkinvent_list")
    permission_required = "inventories.delete_inkinventory"


class InkInventoryDetailView(PermissionMixin, DetailView):
    model = InkInventory
    template_name = "inventory/inkinvent_detail.html"
    context_object_name = "ink"
    permission_required = "inventories.view_inkinventory"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["requests"] = self.object.requests.select_related("requested_by").order_by("-created_at")
        return context


class InkInventoryRequestView(PermissionMixin, CreateView):
    model = InkRequest
    form_class = InkRequestForm
    template_name = "inventory/form.html"
    permission_required = "inventories.add_inkrequest"

    def get_success_url(self):
        return reverse_lazy("inkinvent_detail", kwargs={"pk": self.kwargs["ink_id"]})

    def form_valid(self, form):
        ink = get_object_or_404(InkInventory, pk=self.kwargs["ink_id"])
        form.instance.ink = ink
        try:
            response = super().form_valid(form)
            messages.success(self.request, _("Ink request recorded successfully."))
            return response
        
        except ValueError as e:
            form.add_error("quantity_used", str(e))
            return self.form_invalid(form)



# --- Office Supplies ---
class OfficeSupplyCategoryDeleteView(PermissionMixin, DeleteView):
    model = OfficeSupplyCategory
    template_name = "inventory/delete.html"
    success_url = reverse_lazy("supplycategory_manage")
    permission_required = "inventories.delete_officesupplycategory"


class OfficeSupplyListView(PermissionMixin, ListView):
    model = OfficeSupply
    template_name = "inventory/supply_list.html"
    context_object_name = "supplies"
    permission_required = "inventories.view_officesupply"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category").order_by("-updated_at")
        category_id = self.request.GET.get("category", "").strip()

        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            queryset = queryset.filter(
                Q(name_en__icontains=search_query) |
                Q(name_ar__icontains=search_query)
            )
        if category_id.isdigit():
            queryset = queryset.filter(category_id=category_id)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = OfficeSupplyCategory.objects.all()
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_category"] = self.request.GET.get("category", "").strip()
        return context


class OfficeSupplyCreateView(PermissionMixin, CreateView):
    model = OfficeSupply
    form_class = OfficeSupplyForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("supply_list")
    permission_required = "inventories.add_officesupply"


class OfficeSupplyUpdateView(PermissionMixin, UpdateView):
    model = OfficeSupply
    form_class = OfficeSupplyForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("supply_list")
    permission_required = "inventories.change_officesupply"


class OfficeSupplyDeleteView(PermissionMixin, DeleteView):
    model = OfficeSupply
    template_name = "inventory/delete.html"
    success_url = reverse_lazy("supply_list")
    permission_required = "inventories.delete_officesupply"
