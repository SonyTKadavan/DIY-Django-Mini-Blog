from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.

class BlogAuthor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, help_text="Enter your bio details here.")
    
    def get_absolute_url(self):
        return reverse('blogger-detail', args=[str(self.id)])
    
    def __str__(self):
        return self.user.username

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('tag-posts', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['name']

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(BlogAuthor, on_delete=models.CASCADE)
    content = models.TextField(help_text="Write your blog post here.")
    post_date = models.DateTimeField(default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    class Meta:
        ordering = ['-post_date']
    
    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])
    
    def __str__(self):
        return self.title
        
    def get_reaction_counts(self):
        """Get counts of each reaction type for this post"""
        counts = {}
        for reaction_type, _ in Reaction.REACTION_CHOICES:
            counts[reaction_type] = self.reactions.filter(reaction_type=reaction_type).count()
        return counts
    
    @property
    def reaction_choices(self):
        """Get the available reaction choices"""
        return Reaction.REACTION_CHOICES

class Comment(models.Model):
    blog = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, help_text="Enter comment about blog here.")
    post_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['post_date']
    
    def __str__(self):
        return f'{self.description[:75]}...'

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('like', '👍 Like'),
        ('love', '❤️ Love'),
        ('laugh', '😄 Laugh'),
        ('wow', '😮 Wow'),
        ('sad', '😢 Sad'),
    ]
    
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']  # One reaction per user per post
    
    def __str__(self):
        return f'{self.user.username} - {self.get_reaction_type_display()} on {self.post.title}'
