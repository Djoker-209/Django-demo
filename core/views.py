import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Article, Category, UserProfile
from .forms import ArticleForm, ContactForm, RegisterForm, ProfileForm


# ── HOME ───────────────────────────────────────────────────────────────────────

def home(request):
    """
    Demonstrates:
    - Reading/writing session data
    - Reading/writing cookies
    - ORM queryset passed to template
    """
    request.session['visits'] = request.session.get('visits', 0) + 1

    context = {
        'visits':          request.session['visits'],
        'theme':           request.COOKIES.get('theme', 'light'),
        'recent_articles': Article.objects
                           .filter(status=Article.STATUS_PUBLISHED)
                           .select_related('author', 'category')[:5],
        'categories':      Category.objects.all(),
    }

    response = render(request, 'core/home.html', context)
    response.set_cookie('theme', 'light', max_age=86400, httponly=False)
    return response


def set_theme(request):
    """Writes a theme cookie and redirects back to home."""
    theme = request.GET.get('theme', 'light')
    response = redirect('home')
    response.set_cookie('theme', theme, max_age=86400 * 30)
    return response


# ── JSON API ───────────────────────────────────────────────────────────────────

def api_articles(request):
    """
    Demonstrates:
    - JsonResponse
    - request.method branching
    - request.body JSON parsing
    - ORM .values()
    """
    if request.method == 'GET':
        data = list(
            Article.objects
            .filter(status=Article.STATUS_PUBLISHED)
            .values('id', 'title', 'author__username', 'created_at')
        )
        for item in data:
            item['created_at'] = item['created_at'].isoformat()
        return JsonResponse({'articles': data})

    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        return JsonResponse({'received': payload}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ── CONTACT ────────────────────────────────────────────────────────────────────

def contact(request):
    """
    Demonstrates:
    - Plain Form (GET = blank, POST = validate)
    - Session write on success
    - messages framework
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            request.session['last_contact_name'] = form.cleaned_data['name']
            messages.success(request, f"Thanks {form.cleaned_data['name']}! Message received.")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


# ── AUTH ───────────────────────────────────────────────────────────────────────

def register_view(request):
    """
    Demonstrates:
    - ModelForm save (creates User row)
    - ORM create for related object (UserProfile)
    - login() to start session immediately after registration
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Welcome! Account created.")
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """
    Demonstrates:
    - authenticate() checks credentials against DB
    - login() creates session and sets sessionid cookie
    - ?next= redirect after login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            error = "Invalid username or password."

    return render(request, 'core/login.html', {'error': error})


def logout_view(request):
    """
    logout() deletes the server-side session and clears the cookie.
    """
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('home')


# ── DASHBOARD ──────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    profile.visit_count += 1
    profile.save(update_fields=['visit_count'])

    my_articles = (
        Article.objects
        .filter(author=request.user)
        .select_related('category')
        .prefetch_related('tags')
    )

    # ── Pagination ──────────────────────────────────────────────────
    from django.core.paginator import Paginator
    paginator = Paginator(my_articles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/dashboard.html', {
        'profile':      profile,
        'my_articles':  page_obj,        # ← now a page object
        'page_obj':     page_obj,
        'is_paginated': paginator.num_pages > 1,
        'session_data': dict(request.session),
        'cookies':      request.COOKIES,
    })

# ── SESSION DEMO ───────────────────────────────────────────────────────────────

@login_required
def session_demo(request):
    """
    Demonstrates explicit session and cookie manipulation.
    ?action=set&key=foo&value=bar
    ?action=delete&key=foo
    ?action=flush
    """
    action = request.GET.get('action')
    key    = request.GET.get('key',   'demo_key')
    value  = request.GET.get('value', 'demo_value')

    if action == 'set':
        request.session[key] = value
        messages.success(request, f"Set session['{key}'] = '{value}'")

    elif action == 'delete':
        request.session.pop(key, None)
        messages.warning(request, f"Deleted session key '{key}'")

    elif action == 'flush':
        request.session.flush()
        messages.error(request, "Session flushed!")

    response = render(request, 'core/session_demo.html', {
        'session_items': dict(request.session),
        'cookies':       request.COOKIES,
    })

    count = int(request.COOKIES.get('cookie_count', 0)) + 1
    response.set_cookie('cookie_count', count)
    return response


# ── ARTICLE CRUD (Class-Based Views) ──────────────────────────────────────────

class ArticleListView(ListView):
    """
    Demonstrates:
    - ORM filter + Q objects (OR search)
    - select_related (avoid N+1)
    - Automatic pagination
    """
    model               = Article
    template_name       = 'core/article_list.html'
    context_object_name = 'articles'
    paginate_by         = 5

    def get_queryset(self):
        qs = (
            Article.objects
            .filter(status=Article.STATUS_PUBLISHED)
            .select_related('author', 'category')
        )
        # search filter
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))

        # category filter  ← NEW
        category_slug = self.request.GET.get('category', '')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query']            = self.request.GET.get('q', '')
        ctx['categories']       = Category.objects.all()
        ctx['active_category']  = self.request.GET.get('category', '')  # ← NEW
        return ctx


class ArticleDetailView(DetailView):
    """
    Demonstrates:
    - ORM get single object (404 if not found)
    - Calling a model method (increment_views)
    """
    model               = Article
    template_name       = 'core/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_views()
        return obj


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """
    Demonstrates:
    - LoginRequiredMixin (CBV auth protection)
    - ModelForm save with author injected before INSERT
    """
    model         = Article
    form_class    = ArticleForm
    template_name = 'core/article_form.html'
    success_url   = reverse_lazy('article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Article created!")
        return super().form_valid(form)


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    """
    Demonstrates:
    - ORM UPDATE
    - Ownership check via get_queryset() filter
    """
    model         = Article
    form_class    = ArticleForm
    template_name = 'core/article_form.html'

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Article updated!")
        return self.object.get_absolute_url()


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    """
    Demonstrates:
    - ORM DELETE
    - Confirmation page on GET, hard delete on POST
    - Ownership check via get_queryset() filter
    """
    model         = Article
    template_name = 'core/article_confirm_delete.html'
    success_url   = reverse_lazy('dashboard')

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def form_valid(self, form):
        messages.warning(self.request, "Article deleted.")
        return super().form_valid(form)
    
@login_required
def profile_edit(request):
    """
    Demonstrates:
    - UpdateView as FBV alternative
    - OneToOneField get_or_create
    - ModelForm save on related object
    """
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/profile_edit.html', {'form': form})