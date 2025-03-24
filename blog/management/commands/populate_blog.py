from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import BlogAuthor, BlogPost, Comment
from django.utils import timezone
from django.db import IntegrityError
import random

class Command(BaseCommand):
    help = 'Populate the blog with sample data'

    def handle(self, *args, **kwargs):
        try:
            # Delete all existing data
            Comment.objects.all().delete()
            BlogPost.objects.all().delete()
            BlogAuthor.objects.all().delete()
            User.objects.all().delete()

            # Create superuser
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user'))

            # Create authors
            authors_data = [
                ('john_doe', 'Tech enthusiast and developer'),
                ('jane_smith', 'Digital marketing specialist'),
                ('alex_tech', 'Data scientist and AI researcher')
            ]

            authors = []
            for username, bio in authors_data:
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123'
                )
                author = BlogAuthor.objects.create(user=user, bio=bio)
                authors.append(author)
                self.stdout.write(self.style.SUCCESS(f'Created author: {username}'))

            # Create blog posts
            posts_data = [
                ('Getting Started with Django',
                 '''Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. 
                 Built by experienced developers, it takes care of much of the hassle of web development, so you can focus on writing 
                 your app without needing to reinvent the wheel.'''),
                ('Modern Web Development',
                 '''Modern web development encompasses many different skills and disciplines in the production 
                 and maintenance of websites. This includes web design, web publishing, web programming, and database management.'''),
                ('Machine Learning Basics',
                 '''Machine learning is a branch of artificial intelligence (AI) and computer science which focuses on the use 
                 of data and algorithms to imitate the way that humans learn, gradually improving its accuracy.'''),
                ('AI in Web Development',
                 '''Artificial Intelligence is revolutionizing web development. From automated testing to intelligent user 
                 interfaces, AI is changing how we build and interact with web applications.''')
            ]

            for title, content in posts_data:
                author = random.choice(authors)
                post = BlogPost.objects.create(
                    title=title,
                    content=content,
                    author=author,
                    post_date=timezone.now()
                )
                self.stdout.write(self.style.SUCCESS(f'Created blog post: {title}'))

                # Add comments to each post
                comments = [
                    "Great article! Very informative.",
                    "Thanks for sharing these insights!",
                    "This helped me understand the concept better.",
                    "Looking forward to more posts like this!"
                ]

                for comment_text in random.sample(comments, 3):
                    Comment.objects.create(
                        blog=post,
                        user=random.choice(User.objects.all()),
                        description=comment_text,
                        post_date=timezone.now()
                    )

            self.stdout.write(self.style.SUCCESS('Successfully populated the blog!'))

        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
