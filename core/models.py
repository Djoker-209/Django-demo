

# Create your models here.
# Concepts:
# - Model class     → maps to a database table
# - Field types     → CharField, TextField, BooleanField, DateTimeField, etc.
# - ForeignKey      → one-to-many relationship (many articles → one author)
# - ManyToManyField → many-to-many relationship (articles ↔ tags)
# - OneToOneField   → extends another model (UserProfile extends User)
# - Meta class      → ordering, verbose names
# - __str__         → human-readable string for admin & shell
# - Model methods   → encapsulate business logic (e.g. increment_views)

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    """Lookup table. Illustrates basic model with unique constraint."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)  # set once on create

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Used in ManyToMany relationship with Article."""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    Core model. Shows:
    - CharField / TextField / BooleanField / DateTimeField
    - ForeignKey (author, category)
    - ManyToManyField (tags)
    - choices (status)
    - auto_now_add vs auto_now
    - get_absolute_url pattern
    """
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    title    = models.CharField(max_length=200)
    body     = models.TextField()
    status   = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)  # set on INSERT only
    updated_at = models.DateTimeField(auto_now=True)      # updated on every SAVE

    # Relationships
    author   = models.ForeignKey(User,     on_delete=models.CASCADE,  related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='articles', null=True, blank=True)
    tags     = models.ManyToManyField(Tag, blank=True, related_name='articles')

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"{self.title} [{self.status}]"

    def get_absolute_url(self):
        # reverse() builds the URL from the named pattern
        return reverse('article_detail', kwargs={'pk': self.pk})

    def increment_views(self):
        """Model method: keeps business logic inside the model."""
        self.view_count += 1
        self.save(update_fields=['view_count'])  # efficient: only updates one column


class UserProfile(models.Model):
    """
    Extends Django's built-in User via OneToOneField.
    Demonstrates: how to add extra fields to User without replacing it.
    """
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio         = models.TextField(blank=True)
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile({self.user.username})"