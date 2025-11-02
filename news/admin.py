from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Subscription, ArticleDispatchLog


# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Role & Permissions', {'fields': ('role', 'is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Subscriptions', {'fields': ('subscribed_publishers', 'subscribed_journalists')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


# Publisher Admin
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    filter_horizontal = ('editors', 'journalists')


# Article Admin
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at', 'updated_at')
    list_filter = ('approved', 'publisher', 'author')
    search_fields = ('title', 'content')
    actions = ['approve_articles']

    def approve_articles(self, request, queryset):
        queryset.update(approved=True)
    approve_articles.short_description = "Mark selected articles as approved"


# Subscription Admin
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'publisher', 'subscribed_at')
    list_filter = ('publisher', 'subscribed_at')
    search_fields = ('user__username', 'publisher__name')


# Article Dispatch Log Admin
class ArticleDispatchLogAdmin(admin.ModelAdmin):
    list_display = ('article', 'reader', 'dispatched_at')
    list_filter = ('dispatched_at', 'reader')
    search_fields = ('article__title', 'reader__username')


# Register all models-
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(ArticleDispatchLog, ArticleDispatchLogAdmin)
