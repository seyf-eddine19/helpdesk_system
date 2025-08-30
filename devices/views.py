from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms import modelformset_factory

from employees.mixins import PermissionMixin
from .models import Device, DeviceType, Custody
from .forms import DeviceForm, DeviceAccessoryFormSet, CustodyForm, DeviceCustodyFormSet


# -------------------------------
# Device Types (manage manually)
# -------------------------------
@login_required
@permission_required("devices.view_devicetype", raise_exception=True)
def devices_type_manage(request):
    edit_id = request.GET.get("edit")
    delete_id = request.GET.get("delete")

    # --- Delete ---
    if delete_id:
        if not request.user.has_perm("devices.delete_devicetype") and not request.user.is_superuser:
            messages.error(request, _("You do not have permission to delete a device type"))
            return redirect("devicestype_manage")

        obj = get_object_or_404(DeviceType, pk=delete_id)
        obj.delete()
        messages.success(request, _("Device type deleted successfully"))
        return redirect("devicestype_manage")

    # --- Add / Edit ---
    if request.method == "POST":
        name_ar = request.POST.get("name_ar")
        name_en = request.POST.get("name_en")

        if edit_id:  # Edit
            if not request.user.has_perm("devices.change_devicetype") and not request.user.is_superuser:
                messages.error(request, _("You do not have permission to edit a device type"))
                return redirect("devicestype_manage")

            obj = get_object_or_404(DeviceType, pk=edit_id)
            obj.name_ar = name_ar
            obj.name_en = name_en
            obj.save()
            messages.success(request, _("Device type updated successfully"))

        else:  # Add
            if not request.user.has_perm("devices.add_devicetype") and not request.user.is_superuser:
                messages.error(request, _("You do not have permission to add a device type"))
                return redirect("devicestype_manage")

            DeviceType.objects.create(name_ar=name_ar, name_en=name_en)
            messages.success(request, _("Device type added successfully"))

        return redirect("devicestype_manage")

    # --- Render ---
    types = DeviceType.objects.all()
    current_edit = None
    if edit_id:
        current_edit = get_object_or_404(DeviceType, pk=edit_id)

    return render(request, "devices/devicetype_manage.html", {
        "device_types": types,
        "current_edit": current_edit,
    })


# -------------------------------
# Devices
# -------------------------------
class DeviceListView(PermissionMixin, ListView):
    model = Device
    template_name = "devices/list.html"
    context_object_name = "devices"
    permission_required = "devices.view_device"
    paginate_by = 10


class DeviceDetailView(PermissionMixin, DetailView):
    model = Device
    template_name = "devices/detail.html"
    context_object_name = "device"
    permission_required = "devices.view_device"


class DeviceCreateView(PermissionMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/form.html"
    success_url = reverse_lazy("device_list")
    permission_required = "devices.add_device"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["accessory_formset"] = DeviceAccessoryFormSet(self.request.POST)
        else:
            context["accessory_formset"] = DeviceAccessoryFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        accessory_formset = context["accessory_formset"]

        if accessory_formset.is_valid():
            self.object = form.save()  # save device first
            accessory_formset.instance = self.object  # link accessories to device
            accessory_formset.save()
            messages.success(self.request, _("Device created successfully"))
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeviceUpdateView(PermissionMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/form.html"
    success_url = reverse_lazy("device_list")
    permission_required = "devices.change_device"

    def form_valid(self, form):
        messages.success(self.request, _("Device updated successfully"))
        return super().form_valid(form)


class DeviceCreateView(PermissionMixin, CreateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/form.html"
    success_url = reverse_lazy("device_list")
    permission_required = "devices.add_device"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["accessory_formset"] = DeviceAccessoryFormSet(self.request.POST)
        else:
            context["accessory_formset"] = DeviceAccessoryFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        accessory_formset = context["accessory_formset"]

        if accessory_formset.is_valid():
            self.object = form.save()
            accessory_formset.instance = self.object
            accessory_formset.save()
            messages.success(self.request, _("Device created successfully"))
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeviceUpdateView(PermissionMixin, UpdateView):
    model = Device
    form_class = DeviceForm
    template_name = "devices/form.html"
    success_url = reverse_lazy("device_list")
    permission_required = "devices.change_device"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["accessory_formset"] = DeviceAccessoryFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["accessory_formset"] = DeviceAccessoryFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        accessory_formset = context["accessory_formset"]

        if accessory_formset.is_valid():
            self.object = form.save()
            accessory_formset.instance = self.object
            accessory_formset.save()
            messages.success(self.request, _("Device updated successfully"))
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class DeviceDeleteView(DeleteView):
    model = Device
    template_name = "devices/confirm_delete.html"
    success_url = reverse_lazy("device_list")
    permission_required = "devices.delete_device"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Device deleted successfully"))
        return super().delete(request, *args, **kwargs)


# -------------------------
# Custody Views
# -------------------------
class CustodyListView(PermissionMixin, ListView):
    model = Custody
    template_name = "custody/list.html"
    context_object_name = "custodies"
    permission_required = "devices.view_custody"
    paginate_by = 10


class CustodyDetailView(PermissionMixin, DetailView):
    model = Custody
    template_name = "custody/detail.html"
    context_object_name = "custody"
    permission_required = "devices.view_custody"


class CustodyCreateView(PermissionMixin, CreateView):
    model = Custody
    form_class = CustodyForm
    template_name = "custody/form.html"
    success_url = reverse_lazy("custody_list")
    permission_required = "devices.add_custody"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["devicecustody_formset"] = DeviceCustodyFormSet(self.request.POST)
        else:
            context["devicecustody_formset"] = DeviceCustodyFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["devicecustody_formset"]
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Custody created successfully."))
            return redirect(self.success_url)
        messages.error(self.request, _("There was an error creating the custody."))
        return self.render_to_response(self.get_context_data(form=form))


class CustodyUpdateView(PermissionMixin, UpdateView):
    model = Custody
    form_class = CustodyForm
    template_name = "custody/form.html"
    success_url = reverse_lazy("custody_list")
    permission_required = "devices.change_custody"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["devicecustody_formset"] = DeviceCustodyFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["devicecustody_formset"] = DeviceCustodyFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["devicecustody_formset"]
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, _("Custody updated successfully."))
            return redirect(self.success_url)
        messages.error(self.request, _("There was an error updating the custody."))
        return self.render_to_response(self.get_context_data(form=form))

class CustodyDeleteView(PermissionMixin, DeleteView):
    model = Custody
    template_name = "custody/delete.html"
    success_url = reverse_lazy("custody_list")
    permission_required = "devices.delete_custody"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Custody deleted successfully"))
        return super().delete(request, *args, **kwargs)
