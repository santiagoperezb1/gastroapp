from django.shortcuts import render
from django.http import HttpResponse

def inicio(request):
    return render(request, 'pages/inicio.html')

def software(request):
    return render(request, 'pages/software.html')

def precios(request):
    return render(request, 'pages/precios.html')   