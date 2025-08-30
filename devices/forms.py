from django import forms
from django.forms import inlineformset_factory
from .models import Device, DeviceAccessory, Custody, DeviceCustody, AccessoryCustody, Status


# Device Form
class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ["name_en", "name_ar", "serial_number", "device_type", "status"]


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
class DeviceCustodyForm1(forms.ModelForm):
    device = forms.ModelChoiceField(
        queryset=Device.objects.filter(status=Status.AVAILABLE),
        label="Device",
    )
    accessories = forms.ModelMultipleChoiceField(
        queryset=DeviceAccessory.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = DeviceCustody
        fields = ["custody", "device", "accessories"]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for option in self.fields["accessories"].queryset:
            self.fields["accessories"].widget.choices.queryset = DeviceAccessory.objects.all()
        self.fields["accessories"].widget.attrs.update({"class": "accessory-checkbox"})

    def save1(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            AccessoryCustody.objects.filter(device_custody=instance).delete()
            for accessory in self.cleaned_data.get("accessories", []):
                AccessoryCustody.objects.create(
                    device_custody=instance,
                    accessory=accessory,
                )
        return instance
    
class DeviceCustodyForm(forms.ModelForm):
    device = forms.ModelChoiceField(
        queryset=Device.objects.filter(status=Status.AVAILABLE),
        label="Device",
    )
    accessories = forms.ModelMultipleChoiceField(
        queryset=DeviceAccessory.objects.select_related("device"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = DeviceCustody
        fields = ["custody", "device", "accessories"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build widget choices manually, injecting `data-device`
        choices = []
        for accessory in self.fields["accessories"].queryset:
            choices.append((
                accessory.pk,
                f"{accessory.name_en} ({accessory.device.name_en})"
            ))

        self.fields["accessories"].widget.choices = choices

        # Attach data-device mapping
        self.fields["accessories"].widget.attrs.update({"class": "accessory-checkbox"})

        # Per-choice attributes (Django >=3.1 supports `option_attrs`)
        self.fields["accessories"].widget.option_attrs = {
            accessory.pk: {"data-device": str(accessory.device_id)}
            for accessory in self.fields["accessories"].queryset
        }

class DeviceCustodyForm(forms.ModelForm):
    device = forms.ModelChoiceField(
        queryset=Device.objects.filter(status=Status.AVAILABLE),
        label="Device",
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

        # Add per-option attributes (Django >=3.1)
        self.fields["accessories"].widget.option_attrs = {
            accessory.pk: {"data-device": str(accessory.device_id)}
            for accessory in self.fields["accessories"].queryset
        }

# Inline formset: multiple devices per custody
DeviceCustodyFormSet = inlineformset_factory(
    Custody,
    DeviceCustody,
    form=DeviceCustodyForm,
    extra=0,
    can_delete=True
)
