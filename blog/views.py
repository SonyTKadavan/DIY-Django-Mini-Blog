from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.db.models import Q
import json
from .models import BlogPost, BlogAuthor, Comment, Tag, Reaction
from .forms import RegistrationForm, BlogPostForm

def custom_logout(request):
    logout(request)
    return redirect('/blog/')

def index(request):
    """View function for home page of site."""
    num_blogs = BlogPost.objects.count()
    num_authors = BlogAuthor.objects.count()
    recent_posts = BlogPost.objects.order_by('-post_date')[:5]
    popular_tags = Tag.objects.all()[:10]
    
    # Ensure tags are properly slugified
    for tag in popular_tags:
        if not tag.slug:
            tag.save()
    
    context = {
        'num_blogs': num_blogs,
        'num_authors': num_authors,
        'recent_posts': recent_posts,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'blog/index.html', context=context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to our blog.')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

class BlogPostListView(ListView):
    model = BlogPost
    paginate_by = 5
    ordering = ['-post_date']
    template_name = 'blog/blogpost_list.html'

class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reaction_choices'] = Reaction.REACTION_CHOICES
        if self.request.user.is_authenticated:
            context['user_reaction'] = Reaction.objects.filter(
                post=self.object,
                user=self.request.user
            ).first()
        context['reaction_counts'] = self.object.get_reaction_counts()
        return context

class BloggerListView(ListView):
    model = BlogAuthor
    template_name = 'blog/blogauthor_list.html'

class BloggerDetailView(DetailView):
    model = BlogAuthor
    template_name = 'blog/blogauthor_detail.html'

class BlogPostCreate(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'
    success_url = reverse_lazy('blogs')

    def form_valid(self, form):
        # Set the author before saving
        author = BlogAuthor.objects.get_or_create(user=self.request.user)[0]
        form.instance.author = author
        messages.success(self.request, 'Blog post created successfully!')
        return super().form_valid(form)

class BlogPostUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blog/blogpost_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author.user

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Blog post updated successfully!')
        return super().form_valid(form)

class BlogPostDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    success_url = reverse_lazy('blogs')
    template_name = 'blog/blogpost_confirm_delete.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author.user

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Blog post deleted successfully!')
        return super().delete(request, *args, **kwargs)

class TagPostListView(ListView):
    model = BlogPost
    template_name = 'blog/tag_posts.html'
    paginate_by = 5
    context_object_name = 'posts'

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(tags=self.tag).order_by('-post_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

class SearchResultsView(ListView):
    model = BlogPost
    template_name = 'blog/search_results.html'
    paginate_by = 10
    context_object_name = 'search_results'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if query:
            # Search in title, content, author name, and tags
            return BlogPost.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(author__user__username__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct().order_by('-post_date')
        return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['total_results'] = self.get_queryset().count()
        return context

@login_required
def create_comment(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        if not description:
            messages.error(request, 'Comment cannot be empty.')
            return redirect('post-detail', pk=pk)
            
        try:
            comment = Comment(
                blog=post,
                user=request.user,
                description=description
            )
            comment.save()
            messages.success(request, 'Comment added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding comment: {str(e)}')
    return redirect('post-detail', pk=pk)

@login_required
def toggle_reaction(request, pk):
    """Handle post reactions"""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method is allowed'
        }, status=405)

    try:
        # Get the post or return 404
        post = get_object_or_404(BlogPost, pk=pk)
        
        # Parse JSON data
        try:
            data = json.loads(request.body)
            reaction_type = data.get('reaction_type')
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        
        # Validate reaction type
        if not reaction_type or reaction_type not in dict(Reaction.REACTION_CHOICES):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid reaction type'
            }, status=400)
        
        # Get or create the reaction
        try:
            reaction = Reaction.objects.filter(
                post=post,
                user=request.user
            ).first()

            if reaction:
                if reaction.reaction_type == reaction_type:
                    # Remove reaction if clicking the same type
                    reaction.delete()
                    user_reaction = None
                else:
                    # Change reaction type if clicking a different one
                    reaction.reaction_type = reaction_type
                    reaction.save()
                    user_reaction = reaction_type
            else:
                # Create new reaction
                Reaction.objects.create(
                    post=post,
                    user=request.user,
                    reaction_type=reaction_type
                )
                user_reaction = reaction_type

            # Get updated counts
            reaction_counts = post.get_reaction_counts()
            
            return JsonResponse({
                'status': 'success',
                'reaction_counts': reaction_counts,
                'user_reaction': user_reaction
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Database error: {str(e)}'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }, status=500)
