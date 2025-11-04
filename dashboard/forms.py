from django import forms
from django.contrib.auth.models import User

from dashboard.models import Link, CustomUser, Payment, PaymentMethod


class LoginForm(forms.Form):
    email = forms.CharField(
        label="Correo electrónico",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Correo electrónico",
                "type": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
                "type": "password",
                "id": "password_login",
            }
        ),
    )


class RegisterForm(forms.Form):
    firstname = forms.CharField(
        label="nombres",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombres",
            }
        ),
    )

    lastname = forms.CharField(
        label="apellidos",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Apellidos",
            }
        ),
    )

    identified = forms.IntegerField(
        label="Cédula de identidad",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Cédula", "type": "number"}
        ),
    )

    phone = forms.IntegerField(
        label="Nro de celular",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nro de celular",
            }
        ),
    )

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Correo electrónico",
                "type": "email",
            }
        ),
    )

    password = forms.CharField(
        label="contraseña",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
                "type": "password",
                "id": "password_register",
            }
        ),
    )


class UserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "required": "true"}
            ),
        }


class CustomUserModelForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["identification", "phone", "state"]
        widgets = {
            "identification": forms.NumberInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "state": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class CustomUserEditModelForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "identification",
            "phone",
        ]
        widgets = {
            "identification": forms.NumberInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "required": "true"}
            ),
        }


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["subtotal", "description", "active"]
        widgets = {
            "subtotal": forms.NumberInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "required": "true", "rows": "4"}
            ),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_subtotal(self):
        subtotal = self.cleaned_data.get("subtotal")
        if subtotal is not None and subtotal > 999:
            raise forms.ValidationError("El monto no puede ser mayor a 999.")
        return subtotal


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["first_name", "last_name", "email", "identity", "phone"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
            "identity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
        }


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ["fullname", "bank", "account_number", "account_type", "cci"]
        widgets = {
            "fullname": forms.TextInput(
                attrs={"class": "form-control", "required": "true"}
            ),
            "bank": forms.Select(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
            "account_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
            "account_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "required": "true",
                }
            ),
            "cci": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
        }
