import json
from ntscraper_Edited.ntscraper import Nitter

def fetch_last_5_tweets(username, instance):
    # Initialize Nitter scraper
    scraper = Nitter(log_level=1, instances=[instance], skip_instance_check=True, web_username="Planet", web_password="Jupiter")

    tweets = scraper.get_tweets(username, number=100, instance=instance, mode="user")

    return tweets["tweets"]


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # Specify the username whose tweets you want to
    username = "SAXweb3"  # Example username
    nitter_instance = "http://89.168.40.57:8080"

    # Fetch the last 5 tweets
    tweets = fetch_last_5_tweets(username, nitter_instance)

    # Save to a JSON file
    output_file = f"{username}_last_tweets.json"
    save_to_json(tweets, output_file)