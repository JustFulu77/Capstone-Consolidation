from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.db.models import Q
from itertools import chain
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserRegistrationForm, ArticleForm, NewsletterForm
from .models import CustomUser, Publisher, Article, Subscription, Newsletter
from .twitter_api import tweet

# ----------------------------
# Home
# ----------------------------
def home(request):
    return render(request, 'news/home.html')


# ----------------------------
# ----------------------------
# Journalist Dashboard
# ----------------------------
"""
 
 Display the dashboard for journalists.

    Only users with the 'Journalist' role can access this view.  
    Shows articles and newsletters authored by the user or associated with publishers the user is assigned to, including independent ones.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the journalist dashboard template with context containing:
            - 'articles': queryset of relevant Article objects
            - 'newsletters': queryset of relevant Newsletter objects
    """
@login_required
def journalist_dashboard(request):
    if request.user.role != 'Journalist':
        messages.error(request, "Access denied.")
        return redirect('home')

    # Only show articles/newsletters under assigned publishers or independent
    assigned_publishers = Publisher.objects.filter(journalists=request.user)

    user_articles = Article.objects.filter(
        Q(author=request.user) | Q(publisher__in=assigned_publishers) | Q(publisher__isnull=True)
    ).distinct().order_by('-created_at')

    user_newsletters = Newsletter.objects.filter(
        Q(author=request.user) | Q(publisher__in=assigned_publishers) | Q(publisher__isnull=True)
    ).distinct().order_by('-created_at')

    context = {'articles': user_articles, 'newsletters': user_newsletters}
    return render(request, 'news/journalist_dashboard.html', context)


# ----------------------------
# Editor Dashboard
# ----------------------------
@login_required
def editor_dashboard(request):
    user = request.user

    if user.role != 'Editor':
        messages.error(request, "Access denied.")
        return redirect('home')

    # Publishers that have selected this editor
    editor_publishers = user.editor_publishers.all()  # ManyToMany relation

    # Articles: unapproved only, assigned publishers OR independent
    unapproved_articles = Article.objects.filter(
        approved=False
    ).filter(
        Q(publisher__in=editor_publishers) | Q(publisher__isnull=True)
    ).order_by('-created_at')

    # Newsletters: same logic
    unapproved_newsletters = Newsletter.objects.filter(
        approved=False
    ).filter(
        Q(publisher__in=editor_publishers) | Q(publisher__isnull=True)
    ).order_by('-created_at')

    context = {
        'articles': unapproved_articles,
        'newsletters': unapproved_newsletters
    }

    return render(request, 'news/editor_dashboard.html', context)

@login_required
def editor_dashboard_action(request, item_type, pk):
    user = request.user
    if user.role != 'Editor':
        messages.error(request, "Access denied.")
        return redirect('home')

    # Determine model
    if item_type == 'article':
        instance = get_object_or_404(Article, pk=pk)
    elif item_type == 'newsletter':
        instance = get_object_or_404(Newsletter, pk=pk)
    else:
        messages.error(request, "Invalid item type.")
        return redirect('editor-dashboard')

    # Ensure editor is allowed to edit this item
    if instance.publisher is not None and user not in instance.publisher.editors.all():
        messages.error(request, "You can only manage items under your publishers.")
        return redirect('editor-dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            instance.approved = True
            if item_type == 'article':
                instance.status = 'published'
                instance.published_at = timezone.now()
                notify_subscribers(instance, 'Article')
            else:
                notify_subscribers(instance, 'Newsletter')
            instance.save()
            messages.success(request, f"{item_type.capitalize()} approved successfully!")
        elif action == 'reject':
            instance.approved = False
            if item_type == 'article':
                instance.status = 'draft'
            instance.save()
            messages.info(request, f"{item_type.capitalize()} rejected.")
        elif action == 'delete':
            instance.delete()
            messages.warning(request, f"{item_type.capitalize()} deleted successfully!")

    return redirect('editor-dashboard')

# ----------------------------
# Publisher Dashboard
# ----------------------------
"""
    Display the dashboard for publishers.

    Only users with the 'Publisher' role can access this view.  
    Allows managing editors and journalists linked to the publisher account:
        - Add or remove users from editors/journalists.
        - View current editors and journalists under the publisher.
    
    Handles GET requests to display data and POST requests to update user roles.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the publisher dashboard template with context containing:
            - 'publisher': Publisher instance linked to the logged-in user
            - 'all_users': queryset of all users eligible to be added
            - 'current_editors': queryset of current editors under the publisher
            - 'current_journalists': queryset of current journalists under the publisher
    """
@login_required
def publisher_dashboard(request):
    if request.user.role != 'Publisher':
        messages.error(request, "Access denied.")
        return redirect('home')

    try:
        publisher = Publisher.objects.get(owner=request.user)
    except Publisher.DoesNotExist:
        messages.error(request, "No publisher account linked to your user. Please register or contact admin.")
        return redirect('home')

    all_users = CustomUser.objects.exclude(pk=request.user.pk).filter(role__in=['Editor', 'Journalist'])
    current_editors = publisher.editors.all()
    current_journalists = publisher.journalists.all()

    if request.method == 'POST':
        add_user_id = request.POST.get('add_user')
        remove_user_id = request.POST.get('remove_user')
        role_type = request.POST.get('role_type')

        if add_user_id:
            user_to_add = get_object_or_404(CustomUser, pk=add_user_id, role=role_type)
            if role_type == 'Editor':
                publisher.editors.add(user_to_add)
            elif role_type == 'Journalist':
                publisher.journalists.add(user_to_add)
            messages.success(request, f"{user_to_add.username} added to {role_type.lower()}s.")
            return redirect('publisher-dashboard')

        if remove_user_id:
            user_to_remove = get_object_or_404(CustomUser, pk=remove_user_id, role=role_type)
            if role_type == 'Editor':
                publisher.editors.remove(user_to_remove)
            elif role_type == 'Journalist':
                publisher.journalists.remove(user_to_remove)
            messages.success(request, f"{user_to_remove.username} removed from {role_type.lower()}s.")
            return redirect('publisher-dashboard')

    context = {
        'publisher': publisher,
        'all_users': all_users,
        'current_editors': current_editors,
        'current_journalists': current_journalists
    }
    return render(request, 'news/publisher_dashboard.html', context)



class RoleBasedLoginView(LoginView):
    """
    Custom login view that redirects users based on their role after authentication.

    Roles handled:
        - Editor -> redirects to /editor/
        - Journalist -> redirects to /journalist/
        - Publisher -> redirects to /publisher/
        - Others -> redirects to /articles/

    Methods:
        get_redirect_url(): Determines the URL to redirect the user to after login.
    """

    def get_redirect_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'Editor':
                return '/editor/'
            elif user.role == 'Journalist':
                return '/journalist/'
            elif user.role == 'Publisher':
                return '/publisher/'
            else:
                return '/articles/'
        return super().get_redirect_url()


# ----------------------------
# Helper function for notifications
# ----------------------------
def notify_subscribers(content_obj, type_name):
    try:
        message = f"New {type_name} published: {content_obj.title}"
        tweet(message)
    except Exception as e:
        print(f"Error tweeting {type_name}: {e}")

    if type_name == 'Article':
        subscribers_authors = Subscription.objects.filter(author=content_obj.author)
        subscribers_publishers = Subscription.objects.filter(publisher=content_obj.publisher)
    else:
        subscribers_authors = Subscription.objects.filter(author=content_obj.author)
        subscribers_publishers = Subscription.objects.filter(publisher=content_obj.publisher)

    recipients = set()
    for sub in subscribers_authors:
        if sub.user.wants_notifications:
            recipients.add(sub.user.email)
    for sub in subscribers_publishers:
        if sub.user.wants_notifications:
            recipients.add(sub.user.email)

    if recipients:
        subject = f"New {type_name} Published!"
        message = f"Hi, a new {type_name.lower()} titled '{content_obj.title}' has been published.\n\nCheck it out on our platform!"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, list(recipients), fail_silently=True)


# ----------------------------
# Article Views
# ----------------------------
@login_required
def create_article(request):
    # Prevent Editors from creating articles
    if request.user.role == 'Editor':
        messages.error(request, "Editors are not allowed to create articles.")
        return redirect('editor-dashboard')

    if request.method == 'POST':
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully and pending editor approval!')
            return redirect('journalist-dashboard')
    else:
        form = ArticleForm(user=request.user)

    return render(request, 'news/create_article.html', {'form': form})


from django.utils import timezone

@login_required
def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Editor
    if request.user.role == 'Editor':
        if article.publisher is None or request.user in article.publisher.editors.all():
            if request.method == 'POST':
                form = ArticleForm(request.POST, instance=article, user=request.user)
                if form.is_valid():
                    article = form.save(commit=False)
                    action = request.POST.get('action')

                    if action == 'approve':
                        article.approved = True
                        article.status = 'published'
                        article.published_at = timezone.now()
                        article.save()
                        notify_subscribers(article, 'Article')
                        messages.success(request, 'Article approved, published, and notifications sent!')

                    elif action == 'reject':
                        article.approved = False
                        article.status = 'draft'
                        article.save()
                        messages.info(request, 'Article sent back to draft.')

                    elif action == 'save':
                        article.approved = False
                        article.status = 'draft'
                        article.save()
                        messages.info(request, 'Article updated and pending approval.')

                    return redirect('editor-dashboard')
            else:
                form = ArticleForm(instance=article, user=request.user)

            context = {'form': form, 'article': article, 'role': 'Editor'}
            return render(request, 'news/edit_article.html', context)
        else:
            messages.error(request, "You can only edit articles under your publisher.")
            return redirect('editor-dashboard')

    # Journalist
    elif request.user == article.author:
        if request.method == 'POST':
            form = ArticleForm(request.POST, instance=article, user=request.user)
            if form.is_valid():
                article = form.save(commit=False)
                article.approved = False
                article.status = 'draft'
                article.save()
                messages.info(request, 'Article updated and pending editor approval.')
                return redirect('journalist-dashboard')
        else:
            form = ArticleForm(instance=article, user=request.user)

        context = {'form': form, 'article': article, 'role': 'Journalist'}
        return render(request, 'news/edit_article.html', context)

    else:
        messages.error(request, "You do not have permission to edit this article.")
        return redirect('home')


@login_required
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user == article.author or request.user.role == 'Editor':
        article.delete()
        messages.success(request, 'Article deleted successfully!')
    else:
        messages.error(request, "You do not have permission to delete this article.")
    return redirect('journalist-dashboard' if request.user.role == 'Journalist' else 'editor-dashboard')


# ----------------------------
# Newsletter Views
# ----------------------------
@login_required
def create_newsletter(request):
    # Prevent Editors from creating newsletters
    if request.user.role == 'Editor':
        messages.error(request, "Editors are not allowed to create newsletters.")
        return redirect('editor-dashboard')

    if request.method == 'POST':
        form = NewsletterForm(request.POST, user=request.user)  # pass user
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.author = request.user
            newsletter.approved = False  # ensure pending approval
            newsletter.save()
            messages.success(request, 'Newsletter created successfully and pending editor approval!')
            return redirect('journalist-dashboard')
    else:
        form = NewsletterForm(user=request.user)  # pass user on GET

    return render(request, 'news/create_newsletter.html', {'form': form})


@login_required
def edit_newsletter(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Editor
    if request.user.role == 'Editor':
        if newsletter.publisher is None or request.user in newsletter.publisher.editors.all():
            if request.method == 'POST':
                form = NewsletterForm(request.POST, instance=newsletter, user=request.user)
                if form.is_valid():
                    newsletter = form.save(commit=False)
                    action = request.POST.get('action')

                    if action == 'approve':
                        newsletter.approved = True
                        newsletter.save()
                        notify_subscribers(newsletter, 'Newsletter')
                        messages.success(request, 'Newsletter approved and notifications sent!')
                    elif action == 'reject':
                        newsletter.approved = False
                        newsletter.save()
                        messages.info(request, 'Newsletter rejected.')
                    elif action == 'save':
                        newsletter.approved = False
                        newsletter.save()
                        messages.info(request, 'Newsletter updated and pending approval.')

                    return redirect('editor-dashboard')
            else:
                form = NewsletterForm(instance=newsletter, user=request.user)

            context = {'form': form, 'newsletter': newsletter, 'role': 'Editor'}
            return render(request, 'news/edit_newsletter.html', context)

        else:
            messages.error(request, "You can only edit newsletters under your publisher.")
            return redirect('editor-dashboard')

    # Journalist
    elif request.user == newsletter.author:
        if request.method == 'POST':
            form = NewsletterForm(request.POST, instance=newsletter, user=request.user)
            if form.is_valid():
                newsletter = form.save(commit=False)
                newsletter.approved = False
                newsletter.save()
                messages.info(request, 'Newsletter updated and pending editor approval.')
                return redirect('journalist-dashboard')
        else:
            form = NewsletterForm(instance=newsletter, user=request.user)

        context = {'form': form, 'newsletter': newsletter, 'role': 'Journalist'}
        return render(request, 'news/edit_newsletter.html', context)

    else:
        messages.error(request, "You do not have permission to edit this newsletter.")
        return redirect('home')


@login_required
def delete_newsletter(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.user == newsletter.author or request.user.role == 'Editor':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted successfully!')
    else:
        messages.error(request, "You do not have permission to delete this newsletter.")
    return redirect('journalist-dashboard' if request.user.role == 'Journalist' else 'editor-dashboard')


# ----------------------------
# Authentication
# ----------------------------
def register(request):
    if request.method == 'POST':
        user_form = CustomUserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()  # form now handles Publisher creation
            login(request, user)
            messages.success(request, f"Account created successfully as {user.role}.")

            if user.role == 'Publisher':
                return redirect('publisher-dashboard')
            elif user.role == 'Editor':
                return redirect('editor-dashboard')
            elif user.role == 'Journalist':
                return redirect('journalist-dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = CustomUserRegistrationForm()

    return render(request, 'news/register.html', {'user_form': user_form})



# ----------------------------
# Reader Views
# ----------------------------
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, approved=True)
    return render(request, 'news/article_detail.html', {'article': article})


def reader_articles(request):
    approved_articles = Article.objects.filter(approved=True).order_by('-created_at')
    approved_newsletters = Newsletter.objects.filter(approved=True).order_by('-created_at')

    combined = sorted(
        chain(approved_articles, approved_newsletters),
        key=lambda obj: obj.created_at,
        reverse=True
    )

    combined_with_type = []
    for obj in combined:
        if isinstance(obj, Article):
            combined_with_type.append({'type': 'Article', 'object': obj})
        else:
            combined_with_type.append({'type': 'Newsletter', 'object': obj})

    context = {
        'articles': approved_articles,
        'newsletters': approved_newsletters,
        'combined': combined_with_type
    }

    return render(request, 'news/reader_articles.html', context)


def newsletter_detail(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    context = {'newsletter': newsletter}
    return render(request, 'news/newsletter_detail.html', context)


# ----------------------------
# Subscriptions
# ----------------------------
@login_required
def subscribe_author(request, author_id):
    author = get_object_or_404(CustomUser, pk=author_id, role__in=['Journalist', 'Editor'])
    if request.user.role == 'Reader':
        Subscription.objects.get_or_create(user=request.user, author=author)
        messages.success(request, f'Subscribed to author {author.username}!')
    return redirect('reader-articles')


@login_required
def subscribe_publisher(request, publisher_id):
    publisher = get_object_or_404(Publisher, pk=publisher_id)
    if request.user.role == 'Reader':
        Subscription.objects.get_or_create(user=request.user, publisher=publisher)
        messages.success(request, f'Subscribed to publisher {publisher.name}!')
    return redirect('reader-articles')
