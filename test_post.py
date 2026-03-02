import os
from dotenv import load_dotenv
import tweepy

# load environment variables
load_dotenv()

#Read keys from .env
api_key = os.getenv("X_API_KEY")
api_secret = os.getenv("X_API_SECRET")
access_token = os.getenv("X_ACCESS_TOKEN")
access_secret = os.getenv("X_ACCESS_SECRET")

# Authenticate
client = tweepy.Client(
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret
)

# Test tweet
try:
    response = client.create_tweet(
        text="Hello! This is a test post from my bot"
    )
    print("Tweet posted successfully!")
    print(response) 
except Exception as e:
    print("Error posting tweet:", e)
