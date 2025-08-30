from django import forms
from .models import InkCategory, InkInventory, OfficeSupplyCategory, OfficeSupply


class InkCategoryForm(forms.ModelForm):
    class Meta:
        model = InkCategory
        fields = ["name_ar", "name_en"]


class InkInventoryForm(forms.ModelForm):
    class Meta:
        model = InkInventory
        fields = ["name_ar", "name_en", "category", "quantity"]


class OfficeSupplyCategoryForm(forms.ModelForm):
    class Meta:
        model = OfficeSupplyCategory
        fields = ["name_ar", "name_en"]


class OfficeSupplyForm(forms.ModelForm):
    class Meta:
        model = OfficeSupply
        fields = ["name_ar", "name_en", "category", "quantity"]
