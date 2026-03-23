from django.urls import path
from . import views

urlpatterns = [
    # ── Public pages ───────────────────────────────────────────────
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('set-theme/', views.set_theme, name='set_theme'),

    # ── Authentication ──────────────────────────────────────────────
    path('register/', views.register_view, name='register'),
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),

    # ── Protected pages ─────────────────────────────────────────────
    path('dashboard/',    views.dashboard,    name='dashboard'),
    path('session-demo/', views.session_demo, name='session_demo'),

    # ── Articles CRUD ───────────────────────────────────────────────
    path('articles/',                 views.ArticleListView.as_view(),   name='article_list'),
    path('articles/create/',          views.ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/',        views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<int:pk>/edit/',   views.ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
 

    # ── JSON API ────────────────────────────────────────────────────
    path('api/articles/', views.api_articles, name='api_articles'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]