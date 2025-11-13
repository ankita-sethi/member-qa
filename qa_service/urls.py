from django.urls import path
from api.views import ask
from django.shortcuts import render

def home(request):
    return render(request, "index.html")

urlpatterns = [
    path('', home, name='home'),
    path('api/ask/', ask),
]
