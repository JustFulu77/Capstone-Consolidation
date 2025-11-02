from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import CustomUser, Publisher, Article

class ArticleAPITestCase(TestCase):
    def setUp(self):
        # Create users
        self.reader = CustomUser.objects.create_user(
            username='reader', password='readerpass', role='Reader'
        )
        self.journalist = CustomUser.objects.create_user(
            username='journalist', password='journalistpass', role='Journalist'
        )
        self.editor = CustomUser.objects.create_user(
            username='editor', password='editorpass', role='Editor'
        )

        # Create publisher
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            description='A test publisher'
        )
        # Assign journalist/editor to publisher
        self.publisher.journalists.add(self.journalist)
        self.publisher.editors.add(self.editor)

        # Create articles
        self.article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=self.journalist,
            publisher=self.publisher,
            approved=True
        )
        self.article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            author=self.journalist,
            publisher=self.publisher,
            approved=False
        )

        # API client
        self.client = APIClient()

    def test_list_articles_authenticated(self):
        self.client.login(username='reader', password='readerpass')
        url = reverse('article-list-create-api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_article_journalist(self):
        self.client.login(username='journalist', password='journalistpass')
        url = reverse('article-list-create-api')
        data = {
            'title': 'New Article',
            'content': 'New content'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 3)
        self.assertEqual(Article.objects.last().author, self.journalist)

    def test_retrieve_article(self):
        url = reverse('article-detail-api', kwargs={'pk': self.article1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article1.title)

    def test_update_article_editor(self):
        self.client.login(username='editor', password='editorpass')
        url = reverse('article-detail-api', kwargs={'pk': self.article2.pk})
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article2.refresh_from_db()
        self.assertEqual(self.article2.title, 'Updated Title')

    def test_delete_article_editor(self):
        self.client.login(username='editor', password='editorpass')
        url = reverse('article-detail-api', kwargs={'pk': self.article2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.filter(pk=self.article2.pk).count(), 0)

    def test_subscriber_articles_reader(self):
        # Reader subscribes to publisher
        self.reader.subscribed_publishers.add(self.publisher)
        self.client.login(username='reader', password='readerpass')
        url = reverse('subscriber-articles-api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return approved article
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.article1.title)

    def test_subscriber_articles_unauthenticated(self):
        url = reverse('subscriber-articles-api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # No subscriptions, should return empty list
        self.assertEqual(len(response.data), 0)
