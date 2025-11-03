import tweepy

# Your existing credentials (keep these as they are)
API_KEY = "ulX3lCDJgsnokKj2Qcw2lsGS"
API_KEY_SECRET = "bdTVyDdJrQre6lss5RfE5RvpetRB5dkJuIiQlPu7gIEAfcyKcD"
ACCESS_TOKEN = "1423108197037060096-zcf0smP66gHktdCrkIBJmmGk0hEuLv"
ACCESS_TOKEN_SECRET = "wxKE49iGSdCSZ5Wg9AlFjZIABBqapbvH5KSLL5nVAfGh5"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAh4wEAAAAAZh3EAMJRvrNG6Jd9MXP0ei5MwoQ%3Dkr20wPOlIlqOez9mrFrBSnVMckWRSK5r2Io9naDcwpJcbESxQu"


# Initialize the Tweepy v2 client
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,          
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

def tweet(message):
    """
    Post a tweet using Twitter/X v2 API.
    """
    try:
        client.create_tweet(text=message)
        print("Tweeted successfully!")
    except Exception as e:
        print(f"Error tweeting: {e}")

if __name__ == "__main__":
    tweet("Success!") 
