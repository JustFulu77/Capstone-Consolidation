from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# ---------------------------------
# Custom User Model
# ---------------------------------
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Reader', 'Reader'),
        ('Publisher', 'Publisher'),
        ('Editor', 'Editor'),
        ('Journalist', 'Journalist'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    # Reader-specific fields
    subscribed_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='subscribed_readers'
    )
    subscribed_authors = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='author_subscribers'
    )

    # Reader opt-in for email notifications
    wants_notifications = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Clean up irrelevant fields per role
        if self.role == 'Reader':
            self.subscribed_authors.clear()
        elif self.role in ['Journalist', 'Editor']:
            self.subscribed_publishers.clear()
            self.subscribed_authors.clear()

    def __str__(self):
        return self.username


# ---------------------------------
# Publisher Model
# ---------------------------------
class Publisher(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='publisher_logos/', blank=True, null=True)

    # New: Publisher ownership (so a Publisher can log in)
    owner = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='owned_publisher'
    )

    # Existing: manage editors/journalists
    editors = models.ManyToManyField(CustomUser, related_name='editor_publishers', blank=True)
    journalists = models.ManyToManyField(CustomUser, related_name='journalist_publishers', blank=True)

    def __str__(self):
        return self.name


# ---------------------------------
# Article Model
# ---------------------------------
class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    is_newsletter = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='articles')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='articles', null=True, blank=True)

    def __str__(self):
        return self.title


# ---------------------------------
# Newsletter Model
# ---------------------------------
class Newsletter(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='newsletters')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, related_name='newsletters', null=True, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# ---------------------------------
# Subscription Model
# ---------------------------------
class Subscription(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='subscriptions')
    subscribed_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.publisher:
            return f"{self.user.username} subscribed to publisher {self.publisher.name}"
        elif self.author:
            return f"{self.user.username} subscribed to author {self.author.username}"
        else:
            return f"{self.user.username} has an empty subscription"


# ---------------------------------
# Article Dispatch Log
# ---------------------------------
class ArticleDispatchLog(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    reader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    dispatched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.article.title} sent to {self.reader.username if self.reader else 'N/A'}"
