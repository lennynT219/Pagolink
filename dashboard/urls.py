from django.contrib.auth import views as auth_views
from django.urls import path, re_path

from .templates.user_views import *
from .views import *

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("contrato", ContractView.as_view(), name="contract"),
    path("iniciar-sesion", LoginView.as_view(), name="login"),
    path("registrate", RegisterView.as_view(), name="register"),
    path("cerrar-sesion", LogoutView.as_view(), name="logout"),
    path("vendedores", CustomerView.as_view(), name="customers"),
    path("vendedores/nuevo", AddCustomerView.as_view(), name="customers_add"),
    path(
        "vendedores/editar/<int:pk>", EditCustomerView.as_view(), name="customers_edit"
    ),
    path(
        "vendedores/perfil/<int:pk>",
        CustomerProfileView.as_view(),
        name="customers_profile",
    ),
    path("links", LinkView.as_view(), name="links"),
    path("links/nuevo", LinkAddView.as_view(), name="links_add"),
    path("links/eliminar/<int:pk>", LinkDeleteView.as_view(), name="links_delete"),
    path("links/editar/<int:pk>", LinkUpdateView.as_view(), name="links_update"),
    path("links/<int:pk>", LinkDetailView.as_view(), name="links_detail"),
    path("ventas", SaleView.as_view(), name="sales"),
    path("ventas/exportar", export_view, name="sales_export"),
    path("ventas/<int:pk>", SaleDetailView.as_view(), name="sales_detail"),
    path(
        "solicitud-de-devolucion/<int:pk>", RefundSendView.as_view(), name="refund_send"
    ),
    path("devoluciones", RefundView.as_view(), name="refunds"),
    path("devoluciones/todos", RefundAdminView.as_view(), name="refunds_admin"),
    path(
        "devoluciones/todos/<int:pk>",
        RefundAdminDetailView.as_view(),
        name="refunds_admin_detail",
    ),
    path("factura/<int:pk>", InvoiceView.as_view(), name="invoice"),
    path("editar-mis-datos", EditUserView.as_view(), name="user_edit"),
    path("metodo-de-pago", PaymentMethodView.as_view(), name="payment_method"),
    path(
        "metodo-de-pago/actualizar",
        PaymentMethodEditView.as_view(),
        name="payment_method_update",
    ),
    re_path(
        r"^activar-correo/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]+)/$",
        ActivateEmailView.as_view(),
        name="activate_email",
    ),
    path(
        "restablecer-contrasena/",
        auth_views.PasswordResetView.as_view(
            template_name="dashboard/reset_password.html"
        ),
        name="reset_password",
    ),
    path(
        "recuperar-contrasena/enviado/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="dashboard/reset_password_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "recuperar-contrasena/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="dashboard/reset_password_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "recuperar-contrasena/completado/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="dashboard/reset_password_complete.html"
        ),
        name="password_reset_complete",
    ),
]
