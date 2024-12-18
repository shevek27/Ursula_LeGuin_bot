import os
from dotenv import load_dotenv
import tweepy
import random
import time
import re

# load env variables from .env
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def load_quotes_and_sources(file_path):
    quotes_and_sources = {}
    
    try:
        with open(file_path, "r") as file:
            current_quote = []
            for line in file:
                stripped_line = line.strip()
                # detect end of quote (-)
                if re.search(r" - [^-/s].+$", stripped_line):
                    # extract source
                    *quote_parts, source = stripped_line.rsplit(" - ", maxsplit=1)
                    full_quote = " ".join(current_quote + quote_parts).strip()
                    quotes_and_sources[full_quote] = source
                    current_quote = []
                
                else:
                    # add line to current quote
                    current_quote.append(stripped_line)
    except FileNotFoundError:
        print(f"error: {file_path} not found")

    return quotes_and_sources

def load_posted_quotes(log_file):
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            for line in file:
                return set(line.strip())
    else:
        return set()
    
def save_posted_quote(quote, log_file):
    with open(log_file, "a") as file:
        file.write(f"{quote}\n")


def post_random_quote(quotes_and_sources, log_file):
    quotes = list(quotes_and_sources.keys())
    posted_quotes = load_posted_quotes(log_file)
    available_quotes = []
    for quote in quotes:
        if quote not in posted_quotes:
            available_quotes.append(quote)

    if not available_quotes:
        print("no more quotes to post!")
        return
    
    quote = random.choice(available_quotes)
    try:
        api.update_status(quote)
        print(f"tweet posted! tweet: {quote}")
        save_posted_quote(quote, log_file)
    
    except tweepy.TweepyException as e:
        print(f"error posting tweet, {e}")


def main():
    QUOTES_FILE = "ursula_quotes.txt"
    POSTED_LOG_FILE = "posted_ursula_quotes.txt"
    
    quotes_and_sources = load_quotes_and_sources(QUOTES_FILE)

    while True:
        post_random_quote(quotes_and_sources, POSTED_LOG_FILE)
        time.sleep(1200)



if __name__ == "__main__":
    main()