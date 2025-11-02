from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Dashboards
    path('journalist/', views.journalist_dashboard, name='journalist-dashboard'),
    path('editor/', views.editor_dashboard, name='editor-dashboard'),
    path('publisher/', views.publisher_dashboard, name='publisher-dashboard'),

    # Editor Dashboard Actions (Approve/Reject/Delete)
    path(
        'editor/dashboard/action/<str:item_type>/<int:pk>/',
        views.editor_dashboard_action,
        name='editor-dashboard-action'
    ),

    # Articles
    path('create-article/', views.create_article, name='create-article'),
    path('edit-article/<int:pk>/', views.edit_article, name='edit-article'),
    path('delete-article/<int:pk>/', views.delete_article, name='delete-article'),
    path('articles/', views.reader_articles, name='reader-articles'),
    path('article/<int:pk>/', views.article_detail, name='article-detail'),

    # Newsletters
    path('create-newsletter/', views.create_newsletter, name='create-newsletter'),
    path('edit-newsletter/<int:pk>/', views.edit_newsletter, name='edit-newsletter'),
    path('delete-newsletter/<int:pk>/', views.delete_newsletter, name='delete-newsletter'),
    path('newsletter/<int:pk>/', views.newsletter_detail, name='newsletter-detail'),

    # Authentication
    path('login/', views.RoleBasedLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # Subscriptions
    path('subscribe-author/<int:author_id>/', views.subscribe_author, name='subscribe-author'),
    path('subscribe-publisher/<int:publisher_id>/', views.subscribe_publisher, name='subscribe-publisher'),
]
