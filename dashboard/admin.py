from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Link)
admin.site.register(Payment)
admin.site.register(Bank)
admin.site.register(PaymentMethod)
admin.site.register(Refund)
