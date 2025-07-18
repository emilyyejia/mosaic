from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django_countries import countries
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language
import ollama
from collections import Counter
from django.conf import settings
# Initialize the Ollama client
from taggit.models import Tag
import json
from django.conf import settings
import requests
import os

def travel_advisor_search(request):
    query = request.GET.get('country')
    if not query:
        return JsonResponse({'error': 'No country provided'}, status=400)

    url = "https://travel-advisor.p.rapidapi.com/locations/search"
    headers = {
        "X-RapidAPI-Key": settings.TRAVEL_SUGGESTION_API_KEY,
        "X-RapidAPI-Host": "travel-advisor.p.rapidapi.com"
    }
    params = {
        "query": query,
        "limit": 1
    }
    print("HEADERS:", headers)
    
    response = requests.get(url, headers=headers, params=params)
    print("STATUS CODE", response.status_code)
    print("Response text", response.text)

    return JsonResponse(response.json(), status=response.status_code)


def get_translated_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    language_code = get_language()
    ollama_api_endpoint = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    if not language_code or language_code.startswith('en'):
        target_language = 'zh-Hans'
    else:
        target_language = language_code

    try:
        response = requests.post(
            ollama_api_endpoint,
            json={
                "model": "deepseek-r1:1.5b",
                "prompt": f"Translate the following to {target_language}: {post.body}"
            },
            stream=True,
            timeout=30
        )
        response.raise_for_status()

        translated_body = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                translated_body += data.get("response", "")
                if data.get("done", False):
                    break

        if not translated_body.strip():
            translated_body = "Translation not available."
    except Exception as e:
        print(f"Error during Ollama API call: {e}")
        translated_body = "Translation error."

    return JsonResponse({
        'title': post.title,
        'body': translated_body
    })

CONTINENT_COUNTRIES = {
  'Africa': [
    'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM',
    'CG', 'CD', 'CI', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH',
    'GN', 'GW', 'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU',
    'MA', 'MZ', 'NA', 'NE', 'NG', 'RW', 'ST', 'SN', 'SC', 'SL', 'SO',
    'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN', 'UG', 'EH', 'ZM', 'ZW'
  ],
  'Asia': [
    'AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'CY', 'GE',
    'IN', 'ID', 'IR', 'IQ', 'IL', 'JP', 'JO', 'KZ', 'KW', 'KG', 'LA',
    'LB', 'MY', 'MV', 'MN', 'MM', 'NP', 'KP', 'OM', 'PK', 'PS', 'PH',
    'QA', 'SA', 'SG', 'KR', 'LK', 'SY', 'TJ', 'TH', 'TL', 'TR', 'TM',
    'AE', 'UZ', 'VN', 'YE'
  ],
  'Europe': [
    'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK',
    'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI',
    'LT', 'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT',
    'RO', 'RU', 'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'UA', 'GB',
    'VA'
  ],
  'North America': [
    'AG', 'BS', 'BB', 'BZ', 'CA', 'CR', 'CU', 'DM', 'DO', 'SV', 'GD',
    'GT', 'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'KN', 'LC', 'VC', 'TT',
    'US'
  ],
  'South America': [
    'AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE'
  ],
  'Australia': [
    'AU', 'FJ', 'KI', 'MH', 'FM', 'NR', 'NZ', 'PW', 'PG', 'WS', 'SB', 'TO', 'TV', 'VU'
  ],
  'Antarctica': [
    'AQ'
  ]}

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from main_app.models import Post

class Home(LoginView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            return context
        all_posts = Post.objects.exclude(country="").select_related('user')
        user_posts = all_posts.filter(user=self.request.user)
        user_countries = set(str(post.country).upper() for post in user_posts)
        others_posts = all_posts.exclude(user=self.request.user)
        others_countries = set(str(post.country).upper() for post in others_posts)
        shared = user_countries & others_countries
        user_only = user_countries - others_countries
        others_only = others_countries - user_countries
        context['userOnlyCountries'] = list(user_only)
        context['othersOnlyCountries'] = list(others_only)
        context['sharedCountries'] = list(shared)

        return context


def post_detail(request, post_id):  
    post = Post.objects.get(id=post_id)
    comment_form = CommentForm()
    return render(request, 'posts/post_detail.html', {'post': post, 'comment_form': comment_form})
    

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm 
    def form_valid(self, form):
        form.instance.user = self.request.user  
        return super().form_valid(form)

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'body', 'tags', 'country']

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

from django_countries import countries

@login_required
def user_posts(request):
    posts = Post.objects.filter(user=request.user)
    user_country_codes = list(
        posts.exclude(country="").values_list("country", flat=True).distinct())
    user_country_codes = [str(code).upper() for code in user_country_codes] 
    return render(request, 'posts/user_posts.html', {
        'posts': posts,
        'user_countries': user_country_codes,
    })



@login_required
def user_feed(request):
    posts = Post.objects.all()

    selected_continent = request.GET.get("continent")
    selected_country = request.GET.get("country")
    query = request.GET.get("q", "").strip()
    tags_only = request.GET.get("tags_only")
    sort = request.GET.get("sort", "recent")
    continents = list(CONTINENT_COUNTRIES.keys())
    all_countries = list(countries)  # list of (code, name)
    country_name_map = {code: name for code, name in all_countries}
    if selected_country:
        country_codes = [selected_country]
    elif selected_continent:
        country_codes = CONTINENT_COUNTRIES.get(selected_continent, [])
    else:
        country_codes = [code for code, _ in all_countries]
    if selected_continent:
        filtered_countries = [(code, name) for code, name in all_countries if code in CONTINENT_COUNTRIES.get(selected_continent, [])]
    else:
        filtered_countries = all_countries
    posts = posts.filter(country__in=country_codes)
    if query:
        if tags_only:
            posts = posts.filter(tags__name__icontains=query)
        else:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(body__icontains=query) |
                Q(tags__name__icontains=query)
            )
    if sort == "recent":
        posts = posts.order_by("-created_at")
    elif sort == "oldest":
        posts = posts.order_by("created_at")
    user = request.user
    interest_counter = Counter()
    user_post_countries = Post.objects.filter(user=user).values_list('country', flat=True)
    interest_counter.update({code: 2 for code in user_post_countries if code})
    commented_post_ids = Comment.objects.filter(user=user).values_list('post_id', flat=True)
    commented_countries = Post.objects.filter(id__in=commented_post_ids).values_list('country', flat=True)
    interest_counter.update({code: 1 for code in commented_countries if code})
    top_country_codes = [code for code, _ in interest_counter.most_common(3)]
    top_country_names = [dict(countries).get(code, code) for code in top_country_codes]
    context = {
        "posts": posts,
        "continents": list(CONTINENT_COUNTRIES.keys()),
        "countries": list(countries),
        "selected_continent": request.GET.get("continent"),
        "selected_country": request.GET.get("country"),
        "query": request.GET.get("q", "").strip(),
        "tags_only": request.GET.get("tags_only"),
        "sort": request.GET.get("sort", "recent"),
        "country_name_map": {code: name for code, name in countries},
        "top_country_codes": top_country_codes,
        "top_country_names": top_country_names,  
        "TRAVEL_SUGGESTION_API_KEY": settings.TRAVEL_SUGGESTION_API_KEY,
    }
    return render(request, "posts/user_feed.html", context)
    

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

        return redirect('post_detail', post_id=post.id)



class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['text']
    template_name = 'main_app/comment_form.html'

    def get_success_url(self):
        return self.object.post.get_absolute_url()
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user
    

class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'main_app/comment_confirm_delete.html'

    def get_success_url(self):
        return self.object.post.get_absolute_url()
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user
    
def posts_by_tag(request, tag_slug):
    tag = Tag.objects.get(slug=tag_slug)
    posts = Post.objects.filter(tags__in=[tag])
    return render(request, 'posts/posts_by_tag.html', {'tag': tag, 'posts': posts})   
    