from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from employees.views import DashboardView, ProfileUpdateView

urlpatterns = [
    # URL to switch language
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    # Admin
    path("admin/", admin.site.urls),

    # Dashboard / Index
    path("", DashboardView.as_view(), name="dashboard"),

    # Authentication
    path("accounts/login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(template_name="accounts/password_change.html"), name="password_change"),
    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"), name="password_change_done"),

    # User profile
    path("update-profile/", ProfileUpdateView.as_view(), name="update_profile"),

    # Apps
    path("employees/", include("employees.urls")),
    path("tickets/", include("tickets.urls")),
    path("", include("devices.urls")),
    path("inventories/", include("inventories.urls")),
)

# Error handlers
handler403 = "employees.views.error_403"
handler404 = "employees.views.error_404"
handler500 = "employees.views.error_500"
