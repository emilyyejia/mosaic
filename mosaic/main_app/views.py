from django.shortcuts import render
from django.http import HttpResponse



# Define the home view function
def home(request):
    # Send a simple HTML response
    return HttpResponse('<h1>Hello </h1>')

# Create your views here.
