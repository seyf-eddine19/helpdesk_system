from django import forms
from django.forms import inlineformset_factory
from .models import Device, DeviceAccessory, Custody, DeviceCustody, Status


# Device Form
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["name_en", "name_ar", "brand", "serial_number", "it_service_tag", "device_type", "condition", "status", "notes"]


# Device Accessory Form
class DeviceAccessoryForm(forms.ModelForm):
    class Meta:
        model = DeviceAccessory
        fields = ["name_en", "name_ar", "condition", "notes"]


# Inline formset (link accessories to device)
DeviceAccessoryFormSet = inlineformset_factory(
    parent_model=Device,
    model=DeviceAccessory,
    form=DeviceAccessoryForm,
    fields=["name_en", "name_ar", "condition"],
    extra=0,
    can_delete=True
)


# Custody Form
class CustodyForm(forms.ModelForm):
    class Meta:
        model = Custody
        fields = "__all__"
        widgets = {
            "custody_date": forms.DateInput(attrs={"type": "date"}),
            "return_date": forms.DateInput(attrs={"type": "date"}),
        }


# DeviceCustody Form 
class DeviceCustodyForm(forms.ModelForm):
    device = forms.ModelChoiceField(
        queryset=Device.objects.none(),  # will set in __init__
        label="Device",
        disabled=False  # will disable later for existing instance
    )
    accessories = forms.ModelMultipleChoiceField(
        queryset=DeviceAccessory.objects.select_related("device"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = DeviceCustody
        fields = ["device", "accessories"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            # Existing device cannot be changed
            self.fields["device"].queryset = Device.objects.filter(pk=self.instance.device.pk)
            self.fields["device"].disabled = True

            # Pre-select accessories for this custody
            self.fields["accessories"].initial = self.instance.accessories.all()
        else:
            # New custody: show only available devices
            self.fields["device"].queryset = Device.objects.filter(status=Status.AVAILABLE)

        # Add data-device attribute to accessories for JS filtering (optional)
        self.fields["accessories"].widget.option_attrs = {
            accessory.pk: {"data-device": str(accessory.device_id)}
            for accessory in self.fields["accessories"].queryset
        }
    
    def clean_accessories(self):
        selected_accessories = self.cleaned_data.get("accessories")
        device = self.cleaned_data.get("device")

        for accessory in selected_accessories:
            if accessory.device != device:
                raise forms.ValidationError(f"Accessory {accessory} does not belong to the selected device {device}.")

        return selected_accessories
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Update accessories through AccessoryCustody
            instance.accessories.set(self.cleaned_data["accessories"])
        return instance


# Inline formset: multiple devices per custody
DeviceCustodyFormSet = inlineformset_factory(
    Custody,
    DeviceCustody,
    form=DeviceCustodyForm,
    extra=0,
    can_delete=True
)
