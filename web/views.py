from django.shortcuts import render


def webpage(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def services(request):
    return render(request, 'services.html')