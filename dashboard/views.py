import csv

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.core.mail import EmailMessage, send_mail, BadHeaderError
import requests
import json
from django.contrib.auth import logout, authenticate, login as django_login
from django.shortcuts import get_list_or_404, get_object_or_404
from dashboard.forms import *
from dashboard.models import *
from dashboard.tokens import account_activation_token
from dashboard.utils import get_client_ip, get_location_from_ip


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        form = LoginForm()
        context = {"form": form}
        return render(request, "dashboard/login.html", context)

    def post(self, request):
        form = LoginForm(request.POST)
        error_message = []
        if form.is_valid():
            username = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is None:
                error_message.append("Correo o contraseña incorrecta")
            else:
                if user.is_active:
                    django_login(request, user)
                    seller = CustomUser.objects.get(user=user)
                    try:
                        if seller.contract:
                            return redirect("dashboard")
                    except:
                        return redirect("contract")
                else:
                    error_message.append("El usuario no esta activo, ponte en contacto")

        context = {"errors": error_message, "form": form}
        return render(request, "dashboard/login.html", context)


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        form = RegisterForm()
        context = {"form": form}
        return render(request, "dashboard/register.html", context)

    def post(self, request):
        form = RegisterForm(request.POST)
        error_message = []
        if form.is_valid():
            first_name = form.cleaned_data.get("firstname")
            last_name = form.cleaned_data.get("lastname")
            identified = form.cleaned_data.get("identified")
            phone = form.cleaned_data.get("phone")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = User.objects.filter(email=email)

            if user.count() > 0:
                error_message.append("Este correo ya está en uso")
            else:
                if (
                    first_name
                    and last_name
                    and email
                    and password
                    and phone
                    and identified
                ):
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=password,
                    )
                    user_profile = CustomUser()
                    user_profile.user = user
                    user_profile.phone = phone
                    user_profile.identification = identified
                    user_profile.save()
                    django_login(request, user)

                    current_site = get_current_site(request)
                    mail_subject = "Activación de registro en PagoLink."
                    message = render_to_string(
                        "dashboard/email_confirm_template.html",
                        {
                            "domain": current_site.domain,
                            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                            "token": account_activation_token.make_token(user),
                        },
                    )

                    email = EmailMessage(
                        mail_subject,
                        message,
                        "PagoLink <pagoslinkexpress@gmail.com>",
                        to=[
                            email,
                        ],
                    )
                    email.send()

                    return redirect("dashboard")

                else:
                    error_message.append("Complete el formulario de registro")
        context = {"errors": error_message, "form": form}
        return render(request, "dashboard/register.html", context)


class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect("login")


class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)

        try:
            if seller.contract:
                links = Link.objects.filter(seller=seller)
                sales = Payment.objects.filter(seleer=seller, state=True)
                refunds = Refund.objects.filter(seller=seller)
                sale = 0
                refund = 0
                for r in refunds:
                    refund += r.amount

                for s in sales:
                    sale += s.amount
                context = {
                    "links": links,
                    "sale": sale,
                    "refund": refund,
                    "active": seller.state,
                    "email_active": seller.email_active,
                }
                return render(request, "dashboard/dashboard.html", context)
        except:
            return redirect("contract")


class CustomerView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.is_staff:
            customers = CustomUser.objects.filter(user__is_staff=False).order_by("-id")
            print(customers)
            context = {"customers": customers}
            return render(request, "dashboard/customers.html", context)
        else:
            return redirect("logout")


class AddCustomerView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = RegisterForm()
        context = {"form": form}
        return render(request, "dashboard/customer_add.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = RegisterForm(request.POST)
        error_message = []
        if form.is_valid():
            first_name = form.cleaned_data.get("firstname")
            last_name = form.cleaned_data.get("lastname")
            identified = form.cleaned_data.get("identified")
            phone = form.cleaned_data.get("phone")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = User.objects.filter(email=email)

            if user.count() > 0:
                error_message.append("Este correo ya está en uso")
            else:
                if (
                    first_name
                    and last_name
                    and email
                    and password
                    and phone
                    and identified
                ):
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=password,
                    )
                    user_profile = CustomUser()
                    user_profile.user = user
                    user_profile.phone = phone
                    user_profile.identification = identified
                    user_profile.save()

                    context = {"form": RegisterForm(), "success": True}

                    return render(request, "dashboard/customer_add.html", context)

                else:
                    error_message.append(
                        "Complete el formulario para agregar nuevo vendedor"
                    )
        context = {"errors": error_message, "form": form}
        return render(request, "dashboard/customer_add.html", context)


class EditCustomerView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")

        seller = CustomUser.objects.get(pk=pk)
        form_user = UserModelForm(instance=seller.user)
        form_custom = CustomUserModelForm(instance=seller)
        context = {"form_user": form_user, "form_custom": form_custom}
        return render(request, "dashboard/customer_update.html", context)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(pk=pk)
        form_user = UserModelForm(request.POST, instance=seller.user)
        form_custom = CustomUserModelForm(request.POST, instance=seller)
        if form_user.is_valid() and form_custom.is_valid():
            form_user.save()
            form_custom.save()
            return redirect("customers")
        else:
            context = {
                "form_user": form_user,
                "form_custom": form_custom,
                "error": "Completa el formulario de manera correcta",
            }
            return render(request, "dashboard/customer_update.html", context)


class EditUserView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)
        form_user = UserModelForm(instance=seller.user)
        form_custom = CustomUserEditModelForm(instance=seller)
        context = {"form_user": form_user, "form_custom": form_custom}
        return render(request, "dashboard/user_update.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)
        form_user = UserModelForm(request.POST, instance=seller.user)
        form_custom = CustomUserEditModelForm(request.POST, instance=seller)
        if form_user.is_valid() and form_custom.is_valid():
            form_user.save()
            form_custom.save()
            context = {
                "form_user": form_user,
                "form_custom": form_custom,
                "success": True,
            }
            return render(request, "dashboard/user_update.html", context)
        context = {
            "form_user": form_user,
            "form_custom": form_custom,
            "error": "Completa el formulario de manera correcta",
        }
        return render(request, "dashboard/customer_update.html", context)


class CustomerProfileView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(pk=pk)
        links = Link.objects.filter(seller=seller).order_by("-id")
        sales = Payment.objects.filter(seleer=seller, state=True).order_by("-id")

        try:
            contract = Contract.objects.get(seller=seller)
            print(contract)
        except:
            contract = None
        total = 0
        for sale in sales:
            total += sale.amount_client
        context = {
            "seller": seller,
            "links": links,
            "sales": sales,
            "total": total,
            "contract": contract,
        }
        return render(request, "dashboard/customer_profile.html", context)


class LinkView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        seller = CustomUser.objects.get(user=request.user)
        links = Link.objects.filter(seller=seller).order_by("-id")
        context = {"links": links}
        return render(request, "dashboard/links.html", context)


class LinkDetailView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        link = get_object_or_404(Link, pk=pk)
        clients = Client.objects.filter(link=link)
        sales = Payment.objects.filter(link=link)
        total = 0
        for sale in sales:
            total += sale.amount_client

        site = get_current_site(request)
        context = {
            "link": link,
            "clients": clients,
            "sales": sales,
            "total": total,
            "site": site,
        }
        return render(request, "dashboard/link_detail.html", context)


class LinkAddView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)
        try:
            if seller.contract:
                context = {"enabled": seller.email_active}
                return render(request, "dashboard/link_add.html", context)
        except:
            return redirect("contract")

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        data = request.POST.copy()

        try:
            subtotal = float(data.get("subtotal"))
        except (ValueError, TypeError):
            subtotal = None

        if subtotal is None or subtotal > 999:
            seller = CustomUser.objects.get(user=request.user)
            context = {
                "error": "El monto no puede ser mayor a 999.",
                "enabled": seller.email_active,
            }
            return render(request, "dashboard/link_add.html", context)

        include_igv = int(data.get("igv"))
        unique = int(data.get("unique"))
        description = data.get("description")

        firstname = data.get("firstname", None)
        lastname = data.get("lastname", None)
        phone = data.get("phone", None)
        identity = data.get("identity", None)
        email = data.get("email", None)

        link = Link()
        link.subtotal = subtotal
        link.description = description
        link.include_igv = True
        link.amount = subtotal

        if include_igv:
            link.include_igv = False
            igv = (subtotal * 12) / 100
            link.amount = subtotal + igv
            link.igv = igv

        if unique:
            link.unique = True

        seller = CustomUser.objects.get(user=request.user)
        link.seller = seller
        link.save()

        if firstname or lastname or identity or email or phone:
            client = Client()
            if firstname:
                client.first_name = firstname
            if lastname:
                client.last_name = lastname
            if phone:
                client.phone = phone
            if identity:
                client.identity = identity
            if email:
                client.email = email
            client.link = link
            client.save()

        if email and firstname:
            html_message = loader.render_to_string(
                "dashboard/payment_invite.html",
                {
                    "name": firstname,
                    "seller": seller.user.first_name,
                    "ammount_total": str(link.amount),
                    "subtotal": str(link.subtotal),
                    "igv": str(link.igv),
                    "product": link.description,
                    "link": str(link.id),
                },
            )

            try:
                send_mail(
                    "Invitación de pago",
                    html_message,
                    "PagoLink <pagoslinkexpress@gmail.com>",
                    [email],
                    fail_silently=True,
                    html_message=html_message,
                )
            except BadHeaderError:
                print("Error Header")

        context = {"success": True, "enabled": seller.email_active}
        return render(request, "dashboard/link_add.html", context)


class LinkUpdateView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        link = get_object_or_404(Link, pk=pk)
        form = LinkForm(instance=link)
        context = {"link": link, "form": form}

        return render(request, "dashboard/link_update.html", context)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        link = get_object_or_404(Link, pk=pk)
        form = LinkForm(request.POST, instance=link)
        if form.is_valid():
            subtotal = form.cleaned_data.get("subtotal")

            data = request.POST.copy()
            igv = data.get("igv")
            igv = int(igv)

            if not igv:
                link.include_igv = False
                igv = (subtotal * 12) / 100
                link.amount = subtotal + igv
                link.igv = igv
            else:
                link.include_igv = True
                link.igv = 0.0
                link.amount = subtotal

            unique = data.get("unique")
            unique = int(unique)
            if unique:
                link.unique = True
            else:
                link.unique = False

            link.save()
            form.save()

            context = {
                "success": True,
                "form": form,
                "link": link,
            }
            return render(request, "dashboard/link_update.html", context)
        else:
            context = {
                "error": "Completa el formulario de manera correcta",
                "form": form,
                "link": link,
            }
            return render(request, "dashboard/link_update.html", context)


class LinkDeleteView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        customer = CustomUser.objects.get(user=request.user)
        links = Link.objects.filter(seller=customer)
        link = get_object_or_404(Link, pk=pk)
        if link in links:
            link.delete()
        return redirect("links")


class SaleView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        customer = CustomUser.objects.get(user=request.user)
        sales = Payment.objects.filter(seleer=customer, state=True).order_by("-id")
        total = 0
        for sale in sales:
            total += sale.amount_client
        context = {"sales": sales, "total": total}
        return render(request, "dashboard/sales.html", context)


class SaleDetailView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        customer = CustomUser.objects.get(user=request.user)
        sale = get_object_or_404(Payment, pk=pk)

        context = {
            "sale": sale,
        }
        return render(request, "dashboard/sale_detail.html", context)


class LinkPaymentView(View):
    def get(self, request, pk):
        if (
            "first_name" in request.session
            and "last_name" in request.session
            and "identity" in request.session
            and "email" in request.session
            and "phone" in request.session
        ):
            first_name = request.session["first_name"]
            last_name = request.session["last_name"]
            identity = request.session["identity"]
            email = request.session["email"]
            phone = request.session["phone"]
            payment = Payment()
            payment.first_name = first_name
            payment.last_name = last_name
            payment.identity = identity
            payment.phone = phone
            payment.email = email
            form = PaymentForm(instance=payment)
        else:
            form = PaymentForm()

        link = get_object_or_404(Link, pk=pk)
        link.visitors += 1
        link.save()

        context = {
            "form": form,
            "link": link,
        }

        return render(request, "dashboard/link_pay_1.html", context)

    def post(self, request, pk):
        form = PaymentForm(request.POST)
        link = get_object_or_404(Link, pk=pk)
        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            identity = form.cleaned_data.get("identity")
            phone = form.cleaned_data.get("phone")

            request.session["first_name"] = first_name
            request.session["last_name"] = last_name
            request.session["email"] = email
            request.session["identity"] = identity
            request.session["phone"] = phone

            return redirect("link_pay_card", pk=link.id)

        else:
            context = {
                "error": "Por favor completa el formulario de manera correcta",
                "form": form,
                "link": link,
            }
            return render(request, "dashboard/link_pay_1.html", context)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class LinkPaymentCardView(View):
    def get(self, request, pk):
        link = get_object_or_404(Link, pk=pk)
        first_name = request.session["first_name"]
        last_name = request.session["last_name"]
        email = request.session["email"]
        identity = request.session["identity"]
        phone = request.session["phone"]

        # url = "https://eu-prod.oppwa.com/v1/checkouts"  # URL de producción
        url = "https://eu-test.oppwa.com/v1/checkouts"  # URL de prueba
        headers = {
            "Authorization": "Bearer OGE4Mjk0MTg1YTY1YmY1ZTAxNWE2YzhjNzI4YzBkOTV8YmZxR3F3UTMyWA=="
        }

        price_adjustment = "%0.2f" % (link.amount,)

        body = {
            "entityId": "8ac7a4c872ea49770172ed7feaf7174e",  # Entity ID de prueba
            "amount": str(price_adjustment),
            "currency": "USD",
            "paymentType": "DB",
            "customer.givenName": first_name,
            "customer.surname": last_name,
            "customer.ip": get_client_ip(request),
            "customer.merchantCustomerId": "00" + str(link.id),
            "merchantTransactionId": "order_" + str(link.id),
            "customer.email": email,
            "customer.identificationDocType": "IDCARD",
            "customer.identificationDocId": identity,
            "customer.phone": phone,
            "billing.street1": "Quito",
            "billing.country": "EC",
            "customParameters[SHOPPER_MID]": "1000000505",
            "customParameters[SHOPPER_TID]": "PD100406",
            "customParameters[SHOPPER_VERSIONDF]": "2",
            "risk.parameters[USER_DATA2]": "ADREST",
        }

        response = requests.post(url=url, data=body, headers=headers)
        response_data = response.json()

        if response.status_code in [200, 201]:
            checkout_id = response_data.get("id")
            context = {"id": checkout_id, "link": link, "first_name": first_name}
            return render(request, "dashboard/link_pay_2.html", context)
        else:
            return redirect("link_pay", pk=link.id)


class LinkPaymentProcess(View):
    def get(self, request, pk):
        link = get_object_or_404(Link, pk=pk)
        first_name = request.session["first_name"]
        last_name = request.session["last_name"]
        identity = request.session["identity"]
        email = request.session["email"]
        phone = request.session["phone"]
        errors = []

        try:
            parameters = request.GET.copy()
            resource_path = parameters["resourcePath"]
            entity_id = "8ac7a4c872ea49770172ed7feaf7174e"
            auth_token = (
                "Bearer OGE4Mjk0MTg1YTY1YmY1ZTAxNWE2YzhjNzI4YzBkOTV8YmZxR3F3UTMyWA=="
            )
            url = f"https://eu-test.oppwa.com{resource_path}?entityId={entity_id}"  # URL de prueba

            headers = {
                "Authorization": auth_token,
            }
            response = requests.get(url=url, headers=headers)
            message = response.json()
            result_code = message["result"]["code"]
            print("Mensaje de respuesta:", message)

            if result_code in ["000.100.110", "000.000.000", "000.100.112"]:
                transaction_id = message["id"]
                payment = Payment(
                    first_name=first_name,
                    last_name=last_name,
                    identity=identity,
                    link=link,
                    # seller=link.seller,
                    description=link.description,
                    phone=phone,
                    email=email,
                    kushki_token=transaction_id,
                    commission=((link.subtotal * 3) / 100) + 0.20,
                    subtotal=link.subtotal,
                    igv=link.igv,
                    amount=link.amount,
                    amount_client=link.amount - ((link.subtotal * 3) / 100) + 0.20,
                )
                payment.save()

                # Send confirmation email
                ##send_payment_confirmation(payment)

                if link.unique:
                    link.is_payment = True
                    link.active = False
                    link.save()

                return render(
                    request,
                    "dashboard/invoice.html",
                    {"success": True, "payment": payment},
                )
            else:
                error = message["result"]["description"]
                errors.append(error)
                return render(
                    request,
                    "dashboard/link_pay_2.html",
                    {"errors": errors, "link": link, "first_name": first_name},
                )
        except Exception as e:
            errors.append(str(e))
            return render(
                request,
                "dashboard/link_pay_2.html",
                {"errors": errors, "link": link, "first_name": first_name},
            )


class InvoiceView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        customer = CustomUser.objects.get(user=request.user)
        sales = Payment.objects.filter(seleer=customer)
        sale = get_object_or_404(Payment, pk=pk)
        if sale in sales:
            context = {
                "payment": sale,
            }
            return render(request, "dashboard/invoice.html", context)
        else:
            context = {
                "private": True,
            }
            return render(request, "dashboard/invoice.html", context)


class PaymentMethodView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = PaymentMethodForm()
        seller = CustomUser.objects.get(user=request.user)
        try:
            payment_method = seller.paymentmethod
        except:
            payment_method = None
        context = {"form": form, "bank": payment_method}
        return render(request, "dashboard/payment_method.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        seller = CustomUser.objects.get(user=request.user)
        form = PaymentMethodForm(request.POST)
        if form.is_valid():
            account = form.save()
            account.seller = seller
            account.save()
            context = {"success": True, "form": form}
            return render(request, "dashboard/payment_method.html", context)
        else:
            context = {
                "errors": "Por favor complete el fomulario correctamente",
                "form": form,
            }
            return render(request, "dashboard/payment_method.html", context)


class PaymentMethodEditView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)
        if not seller.paymentmethod:
            return redirect("payment_method")
        form = PaymentMethodForm(instance=seller.paymentmethod)
        context = {
            "form": form,
        }
        return render(request, "dashboard/payment_method.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")

        seller = CustomUser.objects.get(user=request.user)
        form = PaymentMethodForm(request.POST, instance=seller.paymentmethod)
        if form.is_valid():
            form.save()
            context = {"success": True, "form": form}
            return render(request, "dashboard/payment_method.html", context)
        else:
            context = {
                "errors": "Por favor complete el fomulario correctamente",
                "form": form,
            }
            return render(request, "dashboard/payment_method.html", context)


class RefundView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)
        refunds = Refund.objects.filter(seller=seller).order_by("-id")
        total = 0
        for refund in refunds:
            total += refund.amount
        context = {"refunds": refunds, "total": total}
        return render(request, "dashboard/refunds.html", context)


class RefundSendView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        payment = get_object_or_404(Payment, pk=pk)

        description = request.GET.get("description", "")
        succes = False
        refund = Refund()
        if description:
            refund.amount = payment.amount
            refund.seller = payment.seleer
            refund.first_name = payment.first_name
            refund.last_name = payment.last_name
            refund.description = description
            refund.email = payment.email
            refund.phone = payment.phone
            refund.identity = payment.identity
            refund.payment = payment
            refund.save()

            payment.state = False
            payment.save()
            succes = True
        context = {"success": succes, "refund": refund}
        return render(request, "dashboard/refund_succes.html", context)


class RefundAdminView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        refunds = Refund.objects.all().order_by("-id")
        total = 0
        for refund in refunds:
            total += refund.amount
        context = {"refunds": refunds, "total": total}
        return render(request, "dashboard/refunds_admin.html", context)


class RefundAdminDetailView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")
        refund = get_object_or_404(Refund, pk=pk)
        context = {"refund": refund}
        return render(request, "dashboard/refund_admin_detail.html", context)

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.is_staff:
            refund = get_object_or_404(Refund, pk=pk)

            url = (
                "https://api-uat.kushkipagos.com/v1/refund/"
                + refund.payment.kushki_token
            )
            headers = {
                "Content-Type": "application/json",
                "Private-Merchant-Id": "b5d491681d91423eb9afc79b72ce8227",
            }

            response = requests.delete(url=url, headers=headers)
            messagge = json.loads(response.text)
            success = False
            failure = True
            error = ""
            if response.status_code == 201 or response.status_code == 200:
                success = True
                failure = False
                ticket = messagge["ticketNumber"]
                refund.state = True
                refund.ticket = ticket
                refund.save()

                mail_subject = "Solicitud nro #" + str(refund.id) + " aprobado"
                message = (
                    "Hola "
                    + refund.seller.user.first_name
                    + ", hemos aprobado tu solicitud de reembolso"
                    ". Tu cliente recibirá el abono dentro de 24 horas máximo."
                )
                email = EmailMessage(
                    mail_subject,
                    message,
                    "PagoLink <pagoslinkexpress@gmail.com>",
                    to=[
                        refund.seller.user.email,
                    ],
                )
                email.send()

            else:
                error = messagge["message"]
            context = {
                "refund": refund,
                "success": success,
                "failure": failure,
                "error": error,
            }
            return render(request, "dashboard/refund_admin_detail.html", context)


def export_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    seller = CustomUser.objects.get(user=request.user)
    sales = Payment.objects.filter(seleer=seller, state=True).order_by("-id")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="ventas-pagolink.csv"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "CEDULA",
            "CLIENTE",
            "CORREO",
            "TELEFONO",
            "FECHA",
            "SUBTOTAL",
            "IVA",
            "COMISION",
            "TOTAL",
        ]
    )
    for sale in sales:
        writer.writerow(
            [
                sale.identity,
                sale.first_name + " " + sale.last_name,
                sale.email,
                sale.phone,
                sale.created_at,
                sale.subtotal,
                sale.igv,
                sale.commission,
                sale.amount_client,
            ]
        )

    return response


class ContractView(View):
    def get(self, request):
        context = {}
        return render(request, "dashboard/contract.html", context)

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        seller = CustomUser.objects.get(user=request.user)
        ip = get_client_ip(request)
        city = get_location_from_ip(str(ip))
        contract = Contract()
        contract.seller = seller
        contract.ip = ip
        contract.city = city
        contract.save()

        context = {"successs": True}
        return render(request, "dashboard/contract.html", context)
