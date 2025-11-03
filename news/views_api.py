from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from .models import Article, Newsletter, Publisher
from .serializers import ArticleSerializer, NewsletterSerializer
from .notifications import notifications as notify_subscribers


# ----------------------------
# Custom Permission
# ----------------------------
class IsJournalistOrReadOnly(permissions.BasePermission):
    """
    Allow only Journalists to create or edit their own content.
    Editors and Readers can only view.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'Journalist'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user and request.user.role == 'Journalist'


# ----------------------------
# Article API
# ----------------------------
class ArticleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsJournalistOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'Editor':
                return Article.objects.all().order_by('-created_at')
            elif user.role == 'Journalist':
                return Article.objects.filter(author=user).order_by('-created_at')
        return Article.objects.filter(approved=True).order_by('-created_at')

    def perform_create(self, serializer):
        publisher, _ = Publisher.objects.get_or_create(name="Old School News")
        article = serializer.save(author=self.request.user, publisher=publisher, approved=False)
        # You can notify subscribers here if you want immediate notification on creation
        # notify_subscribers(article)  # Optional at creation


class ArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsJournalistOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'Editor':
                return Article.objects.all()
            elif user.role == 'Journalist':
                return Article.objects.filter(author=user)
        return Article.objects.filter(approved=True)


# ----------------------------
# Article Approval (Editors only)
# ----------------------------
class ArticleApprovalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'Editor':
            return Response({"error": "Only editors can approve or reject."}, status=status.HTTP_403_FORBIDDEN)

        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"error": "Article not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'approve':
            article.approved = True
            article.published_at = timezone.now()
            article.save()
            notify_subscribers(article)  # Tweet and email
            return Response({"message": "Article approved."})
        elif action == 'reject':
            article.approved = False
            article.save()
            return Response({"message": "Article rejected."})
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# Newsletter API
# ----------------------------
class NewsletterListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NewsletterSerializer
    permission_classes = [IsJournalistOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'Journalist':
            return Newsletter.objects.filter(author=user).order_by('-created_at')
        return Newsletter.objects.none()

    def perform_create(self, serializer):
        publisher, _ = Publisher.objects.get_or_create(name="Old School News")
        newsletter = serializer.save(author=self.request.user, publisher=publisher)
        # notify_subscribers(newsletter)  # Optional at creation


class NewsletterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NewsletterSerializer
    permission_classes = [IsJournalistOrReadOnly]

    def get_queryset(self):
        return Newsletter.objects.filter(author=self.request.user)


# ----------------------------
# Newsletter Approval (Editors only)
# ----------------------------
class NewsletterApprovalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'Editor':
            return Response({"error": "Only editors can approve or reject."}, status=status.HTTP_403_FORBIDDEN)

        try:
            newsletter = Newsletter.objects.get(pk=pk)
        except Newsletter.DoesNotExist:
            return Response({"error": "Newsletter not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        if action == 'approve':
            newsletter.approved = True
            newsletter.save()
            notify_subscribers(newsletter)
            return Response({"message": "Newsletter approved."})
        elif action == 'reject':
            newsletter.approved = False
            newsletter.save()
            return Response({"message": "Newsletter rejected."})
        return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------
# Subscriber Articles View
# ----------------------------
class SubscriberArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        subscribed_publishers = user.subscribed_publishers.all()
        subscribed_authors = user.subscribed_authors.all()
        return Article.objects.filter(
            approved=True
        ).filter(
            Q(publisher__in=subscribed_publishers) | Q(author__in=subscribed_authors)
        ).order_by('-created_at')
