import logging
from django.core.mail import send_mail
from django.conf import settings
from .twitter_api import tweet

logger = logging.getLogger(__name__)

def notifications(content):
    """
    Send tweet and email notifications for an Article or Newsletter.
    """
    # Attempt to tweet
    try:
        tweet(f"New {content.__class__.__name__} published: {content.title} by {content.author.username}")
        logger.info(f"Tweet sent for {content.__class__.__name__}: {content.title}")
    except Exception as e:
        logger.error(f"Error tweeting {content.__class__.__name__} '{content.title}': {e}")

    # Gather subscribers safely
    subscribers = set()
    if content.publisher:
        subscribers.update(content.publisher.subscribed_users.all())
    subscribers.update(content.author.subscribed_users.all())

    # Email each subscriber with logging
    for subscriber in subscribers:
        if subscriber.email:
            try:
                send_mail(
                    subject=f"New {content.__class__.__name__}: {content.title}",
                    message=(
                        f"Hello {subscriber.username},\n\n"
                        f"A new {content.__class__.__name__.lower()} has been published: {content.title}\n\n"
                        f"Read it here: [LINK]"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[subscriber.email],
                    fail_silently=False  # raise exceptions so we can log them
                )
                logger.info(f"Email successfully sent to {subscriber.email} for {content.__class__.__name__} '{content.title}'")
            except Exception as e:
                logger.error(f"Failed to send email to {subscriber.email} for {content.__class__.__name__} '{content.title}': {e}")
