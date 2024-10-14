from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

def inicio(request):
    return render(request, 'pages/inicio.html')

def software(request):
    return render(request, 'pages/software.html')

def precios(request):
    return render(request, 'pages/precios.html')   
