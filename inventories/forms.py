from django import forms
from .models import InkCategory, InkInventory, InkRequest, OfficeSupplyCategory, OfficeSupply


class InkCategoryForm(forms.ModelForm):
    class Meta:
        model = InkCategory
        fields = ["name_ar", "name_en"]


class InkInventoryForm(forms.ModelForm):
    class Meta:
        model = InkInventory
        fields = ["name_ar", "name_en", "category", "quantity"]


class InkRequestForm(forms.ModelForm):
    class Meta:
        model = InkRequest
        fields = ["requested_by", "quantity_used", "reason"]


class OfficeSupplyCategoryForm(forms.ModelForm):
    class Meta:
        model = OfficeSupplyCategory
        fields = ["name_ar", "name_en"]


class OfficeSupplyForm(forms.ModelForm):
    class Meta:
        model = OfficeSupply
        fields = ["name_ar", "name_en", "category", "quantity"]
