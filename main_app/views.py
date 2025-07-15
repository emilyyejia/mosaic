from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Post
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Define the home view function
class Home(LoginView):
    # Send a simple HTML response
    template_name = 'home.html'

# Create your views here.

@login_required
def user_feed(request):
    posts = Post.objects.filter(user=request.user)
    return render(request, 'posts/user_feed.html', {'posts': posts})

def post_detail(request, post_id):  
    post = Post.objects.get(id=post_id)
    return render(request, 'posts/post_detail.html', {'post': post})
    

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'body', 'tags']
    # success_url = '/user_feed/'
    def form_valid(self, form):
        form.instance.user = self.request.user  
        return super().form_valid(form)

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'body', 'tags']

class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/user_feed/'

def signup(request):
    error_message=''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

@login_required
def user_posts(request):
    return render(request, 'posts/user_posts.html') 

@login_required
def user_feed(request):
    posts = Post.objects.all()

    continents = ["Africa", "Asia", "Europe", "North America", "South America", "Australia", "Antarctica"]
    countries = ["United States", "Canada", "United Kingdom", "Germany", "Japan", "Australia"]

    selected_continents = request.GET.getlist('continents')
    selected_countries = request.GET.getlist('countries')

    if selected_continents:
        posts = posts.filter(location__in=selected_continents)
    if selected_countries:
        posts = posts.filter(location__in=selected_countries)

    sort = request.GET.get('sort', 'recent')
    if sort == 'recent':
        posts = posts.order_by('-created_at')
    elif sort == 'oldest':
        posts = posts.order_by('created_at')

    context = {
        'posts': posts,
        'continents': continents,
        'countries': countries,
        'selected_continents': selected_continents,
        'selected_countries': selected_countries,
        'sort': sort,
    }
    return render(request, 'posts/user_feed.html', context)