from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blogs/', views.BlogPostListView.as_view(), name='blogs'),
    path('blogger/<int:pk>/', views.BloggerDetailView.as_view(), name='blogger-detail'),
    path('bloggers/', views.BloggerListView.as_view(), name='bloggers'),
    path('blog/<int:pk>/', views.BlogPostDetailView.as_view(), name='post-detail'),
    path('blog/<int:pk>/comment/', views.create_comment, name='blog-comment'),
    path('post/<int:pk>/react/', views.toggle_reaction, name='toggle-reaction'),
    path('register/', views.register, name='register'),
    path('post/create/', views.BlogPostCreate.as_view(), name='post-create'),
    path('post/<int:pk>/update/', views.BlogPostUpdate.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.BlogPostDelete.as_view(), name='post-delete'),
    path('tag/<slug:slug>/', views.TagPostListView.as_view(), name='tag-posts'),
    path('search/', views.SearchResultsView.as_view(), name='search'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.custom_logout, name='logout'),
]
