from django.contrib.auth.models import User
from django.db import models


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.TextField()
    identification = models.BigIntegerField()
    state = models.BooleanField(default=False)
    email_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name


class Link(models.Model):
    seller = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    include_igv = models.BooleanField()
    subtotal = models.FloatField()
    igv = models.FloatField(default=0.0)
    amount = models.FloatField()
    unique = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    is_payment = models.BooleanField(default=False)
    visitors = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.description if self.description else ""


class Client(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    first_name = models.TextField(null=True, blank=True)
    last_name = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    identity = models.IntegerField(null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.first_name


class Payment(models.Model):
    link = models.ForeignKey(Link, on_delete=models.SET_NULL, null=True, blank=True)
    seleer = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    identity = models.IntegerField()
    phone = models.IntegerField()
    description = models.TextField()
    subtotal = models.FloatField()
    igv = models.FloatField(default=0.0)
    commission = models.FloatField()
    amount_client = models.FloatField()
    amount = models.FloatField()
    kushki_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.BooleanField(default=True)

    def __str__(self):
        return self.first_name + " - " + str(self.amount) + " - "


class Refund(models.Model):
    seller = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    payment = models.OneToOneField(
        Payment, on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField()
    amount = models.FloatField()
    state = models.BooleanField(default=False)  # False = Pending, True = Acepted
    first_name = models.TextField()
    last_name = models.TextField()
    email = models.EmailField()
    identity = models.IntegerField()
    ticket = models.TextField(null=True)
    phone = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description


class Bank(models.Model):
    title = models.TextField()

    def __str__(self):
        return self.title


class PaymentMethod(models.Model):
    seller = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, null=True)
    fullname = models.TextField()
    account_type = models.TextField()
    account_number = models.TextField()
    cci = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.bank.title + " - " + self.account_number


class Contract(models.Model):
    seller = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    ip = models.TextField()
    city = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
