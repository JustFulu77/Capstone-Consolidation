import tweepy

# Replace with your actual credentials
API_KEY = "ulX3lCDJgsnokKj2Qcw2ls2GS"
API_KEY_SECRET = "bdTVyDdJrQre6lss5RfE5RvpetRB5dkJuIiQlPu7gIEAfcyKcD"
ACCESS_TOKEN = "1423108197037060096-zcf0smP66gHktdCrkIBJmmGk0hEuLv"
ACCESS_TOKEN_SECRET = "wxKE49iGSdCSZ5Wg9AlFjZIABBqapbvH5KSLL5nVAfGh5"

auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def tweet(message):
    try:
        api.update_status(message)
        print("Tweeted successfully!")
    except Exception as e:
        print(f"Error tweeting: {e}")
