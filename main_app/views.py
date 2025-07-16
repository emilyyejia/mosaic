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
from taggit.models import Tag



#country dictionary
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

class Home(LoginView):
    template_name = 'home.html'

def post_detail(request, post_id):  
    post = Post.objects.get(id=post_id)
    comment_form = CommentForm()
    return render(request, 'posts/post_detail.html', {'post': post, 'comment_form': comment_form})
    

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm 
    # fields = ['title', 'body', 'tags', 'country', 'image']
    # success_url = '/user_feed/'
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

@login_required
def user_posts(request):
    posts = Post.objects.filter(user=request.user)
    return render(request, 'posts/user_posts.html', {'posts': posts})


@login_required
def user_feed(request):
    posts = Post.objects.all()
    selected_continent = request.GET.get("continent")
    selected_country = request.GET.get("country")
    query = request.GET.get("q", "").strip()
    tags_only = request.GET.get("tags_only")
    sort = request.GET.get("sort", "recent")
    continents = list(CONTINENT_COUNTRIES.keys())
    all_countries = list(countries)
    country_name_map = {code: name for code, name in all_countries}
    if selected_continent:
        codes_in_continent = CONTINENT_COUNTRIES.get(selected_continent, [])
        filtered_countries = [(code, name) for code, name in all_countries if code in codes_in_continent]
    else:
        filtered_countries = all_countries
    if selected_country:
        posts = posts.filter(country=selected_country)
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
    context = {
        "posts": posts,
        "continents": continents,
        "countries": filtered_countries,
        "selected_continent": selected_continent,
        "selected_country": selected_country,
        "query": query,
        "tags_only": tags_only,
        "sort": sort,
        "country_name_map":country_name_map,
    }
    return render(request, "posts/user_feed.html", context)

@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST)
    parent_id = request.POST.get("parent_id")
    
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.post_id = post_id
        new_comment.user = request.user

        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)
            new_comment.parent = parent_comment
        new_comment.save()
    
    return redirect('post_detail', post_id=post_id)


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
    