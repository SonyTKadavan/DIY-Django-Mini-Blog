from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import BlogPost, Tag

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
    
    def clean_name(self):
        name = self.cleaned_data['name']
        # Convert to lowercase and replace spaces with hyphens for slug
        slug = slugify(name)
        # Check if a tag with this slug already exists
        if Tag.objects.filter(slug=slug).exists() and not self.instance.pk:
            raise forms.ValidationError('A tag with this name already exists.')
        return name

class BlogPostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. python, django, web-dev'})
    )
    
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['tags'].initial = ', '.join(t.name for t in self.instance.tags.all())
    
    def clean_tags(self):
        tags_string = self.cleaned_data.get('tags', '')
        if not tags_string:
            return []
        
        tag_names = [name.strip() for name in tags_string.split(',') if name.strip()]
        tags = []
        
        for name in tag_names:
            slug = slugify(name)
            try:
                # Try to get existing tag first
                tag = Tag.objects.get(slug=slug)
            except Tag.DoesNotExist:
                # Create new tag if it doesn't exist
                tag = Tag.objects.create(name=name, slug=slug)
            tags.append(tag)
        
        return tags
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Clear existing tags and add new ones
            instance.tags.clear()
            instance.tags.add(*self.cleaned_data['tags'])
        return instance
