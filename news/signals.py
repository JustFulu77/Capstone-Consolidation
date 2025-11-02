from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import requests

from .models import Article, Subscription, ArticleDispatchLog


@receiver(post_save, sender=Article)
def article_approved(sender, instance, created, **kwargs):
    """
    When an article is approved (approved=True), dispatch it to subscribers via email
    and post to X.
    Only triggers when article transitions from not approved to approved.
    """
    # Only proceed if article is approved and just changed to approved
    if instance.approved and (created or not getattr(instance, "_emails_dispatched", False)):
        
        # Subscribers to publisher
        publisher_subs = Subscription.objects.filter(publisher=instance.publisher) if instance.publisher else Subscription.objects.none()

        # Subscribers to journalist
        journalist_subs = Subscription.objects.filter(user=instance.author)

        all_subs = publisher_subs | journalist_subs

        for sub in all_subs:
            subscriber_email = sub.user.email
            try:
                send_mail(
                    subject=f"New Article: {instance.title}",
                    message=f"{getattr(instance, 'summary', instance.title)}\n\nRead more on our site.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber_email],
                    fail_silently=False,
                )
                # Log dispatch success
                ArticleDispatchLog.objects.create(
                    article=instance,
                    reader=sub.user,
                    dispatched_at=timezone.now()
                )
            except Exception as e:
                # Log dispatch failure
                ArticleDispatchLog.objects.create(
                    article=instance,
                    reader=sub.user,
                    dispatched_at=timezone.now()
                )
                print(f"Failed to send email to {subscriber_email}: {e}")

        # ---- Post to X ----
        X_API_URL = "https://api.twitter.com/2/tweets"
        X_BEARER_TOKEN = getattr(settings, "X_BEARER_TOKEN", None)

        if X_BEARER_TOKEN:
            headers = {
                "Authorization": f"Bearer {X_BEARER_TOKEN}",
                "Content-Type": "application/json",
            }
            payload = {"text": f"New Article Published: {instance.title}"}
            try:
                response = requests.post(X_API_URL, json=payload, headers=headers)
                ArticleDispatchLog.objects.create(
                    article=instance,
                    reader=None,
                    dispatched_at=timezone.now(),
                )
            except Exception as e:
                ArticleDispatchLog.objects.create(
                    article=instance,
                    reader=None,
                    dispatched_at=timezone.now(),
                )
                print(f"Failed to post to X: {e}")

        # Dispatch the email
        instance._emails_dispatched = True
