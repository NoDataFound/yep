import tweepy
import streamlit as st
import re
import requests
from dotenv import load_dotenv, set_key

import os


load_dotenv('.env')

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_SECRET')

if not consumer_key:
    consumer_key = st.text_input("Enter CONSUMER_KEY")
if not consumer_secret:
    consumer_secret = st.text_input("Enter CONSUMER_SECRET")
if not access_token:
    access_token = st.text_input("Enter ACCESS_TOKEN")
if not access_token_secret:  
    access_token_secret = st.text_input("Enter ACCESS_SECRET")
    set_key('.env', 'CONSUMER_KEY', consumer_key)


os.environ['CONSUMER_KEY'] = consumer_key
os.environ['CONSUMER_SECRET'] = consumer_secret
os.environ['ACCESS_TOKEN'] = access_token
os.environ['ACCESS_SECRET'] = access_token_secret
# Enter your Twitter API keys and access tokens


# Authenticate to Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

st.title("Twitter Bot")
st.sidebar.title("Phrases to monitor")
phrases = [
    r"do I have any friends that live in (.+)",
    r"do I have any friends that work for (.+)",
    r"do I know anyone that live (.+)",
    r"do I know anyone that works for (.+)"
]

new_phrase = st.sidebar.text_input("Add new phrase:")
if new_phrase:
    phrases.append(new_phrase)
    st.sidebar.text("Phrase added!")
    st.sidebar.text("Current phrases:")
    for p in phrases:
        st.sidebar.text(p)

def match_tweet(text):
    for phrase in phrases:
        match = re.search(phrase, text)
        if match:
            return match.group(1)
    return None

def search_friends(user, query, search_type):
    friends = []
    for friend in tweepy.Cursor(api.friends, screen_name=user).items():
        if search_type == "location" and query.lower() in friend.location.lower():
            friends.append(friend.screen_name)
        elif search_type == "company" and query.lower() in friend.description.lower():
            friends.append(friend.screen_name)
    return friends

def send_tweet(user, matches):
    if matches:
        match_list = ", ".join(f"@{m}" for m in matches)
        tweet = f"Yep, @{user} you know {match_list}."
        api.update_status(tweet)
class MyStreamListener(StreamListener):
    def on_status(self, status):
        user = status.user.screen_name
        text = status.text
        search_type = "location" if "live" in text else "company"
        query = match_tweet(text)

        if query:
            matches = search_friends(user, query, search_type)
            send_tweet(user, matches)
            st.write(f"Found a tweet from @{user}: {text}")

    def on_error(self, status_code):
        if status_code == 420:
            return False

stream_listener = StreamListener()
stream = tweepy.Stream(auth=api.auth, listener=stream_listener)

# Start the stream
if st.button("Start Listening"):
    st.write("Bot is now listening...")
    stream.filter(track=phrases, is_async=True)

