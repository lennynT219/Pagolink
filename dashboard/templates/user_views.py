from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import force_str as force_text
from django.utils.http import urlsafe_base64_decode
from django.views.generic import View

from dashboard.models import CustomUser
from dashboard.tokens import account_activation_token


class ActivateEmailView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()

            traveler = get_object_or_404(CustomUser, user=user)
            traveler.email_active = True
            traveler.save()

            return render(request, "dashboard/email_active_successfull.html")
        else:
            return HttpResponse("Activación incorrecto!")
