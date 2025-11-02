from rest_framework import serializers
from .models import Article, Newsletter, Publisher, CustomUser

# Article Serializer
class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    publisher = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'content', 'author', 'publisher',
            'approved', 'is_newsletter', 'status', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'author', 'publisher', 'approved', 'created_at', 'updated_at', 'published_at'
        ]


# Newsletter Serializer
class NewsletterSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    publisher = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'content', 'author', 'publisher',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'publisher', 'created_at', 'updated_at'
        ]
