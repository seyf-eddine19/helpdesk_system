from django.urls import path
from . import views

urlpatterns = [
    # Device Types
    path("device-types/", views.devices_type_manage, name="devicestype_manage"),

    # Devices
    path("devices/", views.DeviceListView.as_view(), name="device_list"),
    path("devices/add/", views.DeviceCreateView.as_view(), name="device_add"),
    path("devices/<int:pk>/", views.DeviceDetailView.as_view(), name="device_detail"),
    path("devices/<int:pk>/edit/", views.DeviceUpdateView.as_view(), name="device_edit"),
    path("devices/<int:pk>/delete/", views.DeviceDeleteView.as_view(), name="device_delete"),

    # Custody
    path("custody/", views.CustodyListView.as_view(), name="custody_list"),
    path("custody/add/", views.CustodyCreateView.as_view(), name="custody_add"),
    path("custody/<int:pk>/", views.CustodyDetailView.as_view(), name="custody_detail"),
    path("custody/<int:pk>/edit/", views.CustodyUpdateView.as_view(), name="custody_edit"),
    path("custody/<int:pk>/delete/", views.CustodyDeleteView.as_view(), name="custody_delete"),
    path("custody/<int:pk>/export/<str:action>/", views.CustodyExportView.as_view(), name="custody_export"),
]
