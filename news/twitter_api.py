import tweepy

# Your existing credentials (keep these as they are)
API_KEY = "TULBK5FwFMwb4VH9oR1dPGXcR"
API_KEY_SECRET = "F7Qu5CPWpbtiZ8ngXMqas8dvORtoflkYN1V8UUxNPGy6PiaqmM"
ACCESS_TOKEN = "1423108197037060096-3qyO7LFJgyLU4ctV6Uvf8u6WS7GIq6"
ACCESS_TOKEN_SECRET = "FyU2R86T5Sb4nOcqhiupAIT7LyCXJo3DfwAO77T6uOxHu"


# Initialize the Tweepy v2 client
client = tweepy.Client(     
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    
)  
print(client)

def tweet(message):
    """
    Post a tweet using Twitter/X v2 API.
    """
    try:
        client.create_tweet(text=message, user_auth= True)
        print("Tweeted successfully!")
    except Exception as e:
        print(f"Error tweeting: {e}")

if __name__ == "__main__":
    tweet("Success!") 
