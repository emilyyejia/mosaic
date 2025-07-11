from django.shortcuts import render
from django.contrib.auth.views import LoginView



# Define the home view function
class Home(LoginView):
    # Send a simple HTML response
    template_name = 'home.html'

# Create your views here.

