from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'samples/index.html')

def messages(request):
    return render(request, 'samples/messages.html')