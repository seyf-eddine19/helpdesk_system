from django.urls import path
from . import views

urlpatterns = [
    # --- Ink Categories ---
    path("ink-categories/", views.inkcategory_manage, name="inkcategory_manage"),
    path("ink-categories/<int:pk>/delete/", views.InkCategoryDeleteView.as_view(), name="inkcategory_delete"),

    # --- Ink Inventory ---
    path("inks/", views.InkInventoryListView.as_view(), name="inkinvent_list"),
    path("inks/add/", views.InkInventoryCreateView.as_view(), name="inkinvent_add"),
    path("inks/<int:pk>/edit/", views.InkInventoryUpdateView.as_view(), name="inkinvent_edit"),
    path("inks/<int:pk>/delete/", views.InkInventoryDeleteView.as_view(), name="inkinvent_delete"),

    # --- Office Supply Categories ---
    path("supply-categories/", views.supplycategory_manage, name="supplycategory_manage"),
    path("supply-categories/<int:pk>/delete/", views.OfficeSupplyCategoryDeleteView.as_view(), name="supplycategory_delete"),

    # --- Office Supplies ---
    path("supplies/", views.OfficeSupplyListView.as_view(), name="supply_list"),
    path("supplies/add/", views.OfficeSupplyCreateView.as_view(), name="supply_add"),
    path("supplies/<int:pk>/edit/", views.OfficeSupplyUpdateView.as_view(), name="supply_edit"),
    path("supplies/<int:pk>/delete/", views.OfficeSupplyDeleteView.as_view(), name="supply_delete"),
]
