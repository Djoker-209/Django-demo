# Concepts:
# - ModelForm  → auto-generates fields from a model; saves directly to DB
# - Form       → manual fields; you process data yourself in the view
# - Widget     → controls the HTML element rendered for a field
# - clean_<field>() → field-level validation
# - clean()    → cross-field validation

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Article


class ArticleForm(forms.ModelForm):
    """
    ModelForm: Django reads the model's fields and creates form fields.
    We customise widgets to add Bootstrap classes and placeholders.
    """
    class Meta:
        model = Article
        fields = ['title', 'body', 'category', 'status']
        widgets = {
            'title':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Article title'}),
            'body':     forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status':   forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_title(self):
        """Field-level validation: runs after the field's built-in validation."""
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        return title

    def clean(self):
        """Cross-field validation: runs after all individual field validations."""
        cleaned = super().clean()
        status = cleaned.get('status')
        body   = cleaned.get('body', '')
        if status == Article.STATUS_PUBLISHED and len(body) < 20:
            raise forms.ValidationError(
                "Cannot publish: body is too short (min 20 characters)."
            )
        return cleaned


class ContactForm(forms.Form):
    """
    Plain Form (not model-backed).
    Fields are defined manually; data is processed in the view (not saved to DB).
    """
    name    = forms.CharField(max_length=100,
                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}))
    email   = forms.EmailField(
                widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}))
    message = forms.CharField(min_length=10,
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    subscribe = forms.BooleanField(required=False, label='Subscribe to newsletter?')


class RegisterForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm.
    Adds an email field and applies Bootstrap styling to all fields.
    """
    email = forms.EmailField(required=True,
                widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model  = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap class to every field automatically
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
        }