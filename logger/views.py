from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request, 'logger/login.html')

def setup(request):
    return render(request, 'logger/setup.html')

def verify(request, username, password):
    return render(request, 'logger/verify.html')