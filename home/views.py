from django.shortcuts import render

# Create your views here.
from django.views import View


class IndexView(View):
    def get(self, request):
        context = {

        }
        return render(request, 'home/index.html', context)


class ContactView(View):
    def get(self, request):
        context = {

        }
        return render(request, 'home/contact.html', context)


class PricingView(View):
    def get(self, request):
        context = {

        }
        return render(request, 'home/pricing.html', context)
