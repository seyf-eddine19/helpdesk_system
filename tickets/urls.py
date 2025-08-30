from django.urls import path
from . import views


urlpatterns = [
    # Request Types
    path("request-types/", views.request_type_manage, name="requesttype_manage"),

    # Tickets
    path("", views.TicketListView.as_view(), name="ticket_list"),
    path("add/", views.TicketCreateView.as_view(), name="ticket_add"),
    path("<int:pk>/", views.TicketDetailView.as_view(), name="ticket_detail"),
    path("<int:pk>/edit/", views.TicketUpdateView.as_view(), name="ticket_edit"),
    path("<int:pk>/delete/", views.TicketDeleteView.as_view(), name="ticket_delete"),

    # path("tickets/<int:pk>/assign/", views.ticket_assign, name="ticket_assign"),  # custom action
    # path("tickets/<int:pk>/close/", views.ticket_close, name="ticket_close"),    # custom action
]
