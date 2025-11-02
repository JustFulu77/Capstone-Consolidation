from django.core.mail import send_mail
from django.conf import settings
import requests

def send_article_email(article):
    """
    Sends the approved article to all subscribers
    of the publisher and/or journalist.
    """
    subscribers = set()

    # Subscribers of the publisher
    if article.publisher:
        subscribers.update(article.publisher.subscribers.all())

    # Subscribers of the journalist
    subscribers.update(article.author.subscribers.all())

    for subscriber in subscribers:
        send_mail(
            subject=f"New Article: {article.title}",
            message=f"Dear {subscriber.username},\n\n{article.content}\n\n- {article.author.username}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=False,
        )


def post_to_x(article):
    """
    Posts the approved article to X via its API.
    """
    # Replace with your X API credentials in production
    x_api_url = "https://api.twitter.com/2/tweets"
    x_bearer_token = settings.X_BEARER_TOKEN

    headers = {
        "Authorization": f"Bearer {x_bearer_token}",
        "Content-Type": "application/json",
    }

    data = {
        "text": f"{article.title}\n\n{article.content[:200]}... Read more on our site!"
    }

    response = requests.post(x_api_url, headers=headers, json=data)
    return response.status_code, response.text
