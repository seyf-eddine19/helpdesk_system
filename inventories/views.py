from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import InkCategory, InkInventory, OfficeSupplyCategory, OfficeSupply
from .forms import InkCategoryForm, InkInventoryForm, OfficeSupplyCategoryForm, OfficeSupplyForm

from employees.mixins import PermissionMixin


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
        obj.delete()
        messages.success(request, _("Ink category deleted successfully"))
        return redirect("inkcategory_manage")

    # --- Add / Edit ---
    if request.method == "POST":
        name_ar = request.POST.get("name_ar")
        name_en = request.POST.get("name_en")

        if edit_id:  # Edit
            if not request.user.has_perm("inventories.change_inkcategory") and not request.user.is_superuser:
                messages.error(request, _("You do not have permission to edit an ink category"))
                return redirect("inkcategory_manage")

            obj = get_object_or_404(InkCategory, pk=edit_id)
            obj.name_ar = name_ar
            obj.name_en = name_en
            obj.save()
            messages.success(request, _("Ink category updated successfully"))

        else:  # Add
            if not request.user.has_perm("inventories.add_inkcategory") and not request.user.is_superuser:
                messages.error(request, _("You do not have permission to add an ink category"))
                return redirect("inkcategory_manage")

            InkCategory.objects.create(name_ar=name_ar, name_en=name_en)
            messages.success(request, _("Ink category added successfully"))

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
        obj.delete()
        messages.success(request, _("Supply category deleted successfully"))
        return redirect("supplycategory_manage")

    # --- Add / Edit ---
    if request.method == "POST":
        name_ar = request.POST.get("name_ar")
        name_en = request.POST.get("name_en")

        if edit_id:  # Edit
            if not request.user.has_perm("inventories.change_officesupplycategory") and not request.user.is_superuser:
                messages.error(request, _("You do not have permission to edit a supply category"))
                return redirect("supplycategory_manage")

            obj = get_object_or_404(OfficeSupplyCategory, pk=edit_id)
            obj.name_ar = name_ar
            obj.name_en = name_en
            obj.save()
            messages.success(request, _("Supply category updated successfully"))

        else:  # Add
            if not request.user.has_perm("inventories.add_officesupplycategory") and not request.user.is_superuser:
                messages.error(request, _("You do not have permission to add a supply category"))
                return redirect("supplycategory_manage")

            OfficeSupplyCategory.objects.create(name_ar=name_ar, name_en=name_en)
            messages.success(request, _("Supply category added successfully"))

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
    success_url = reverse_lazy("inkcategory_list")
    permission_required = "inventories.delete_inkcategory"


class InkInventoryListView(PermissionMixin, ListView):
    model = InkInventory
    template_name = "inventory/inkinvent_list.html"
    context_object_name = "inks"
    permission_required = "inventories.view_inkinventory" 


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


# --- Office Supplies ---
class OfficeSupplyCategoryDeleteView(PermissionMixin, DeleteView):
    model = OfficeSupplyCategory
    template_name = "inventory/delete.html"
    success_url = reverse_lazy("supplycategory_list")
    permission_required = "inventories.delete_officesupplycategory"


class OfficeSupplyListView(PermissionMixin, ListView):
    model = OfficeSupply
    template_name = "inventory/supply_list.html"
    context_object_name = "supplies"
    permission_required = "inventories.view_officesupply"


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
