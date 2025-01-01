import requests
import json

# Authentication
def get_access_token(client_id, client_secret, user_agent):
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    headers = {"User-Agent": user_agent}
    data = {"grant_type": "client_credentials"}

    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch access token: {response.status_code} {response.text}")

    return response.json()["access_token"]

# Fetch subreddit posts
def fetch_subreddit_posts(subreddit_name, headers, limit):
    url = f"https://oauth.reddit.com/r/{subreddit_name}/new.json?limit={limit}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch subreddit posts: {response.status_code}")

    posts_data = response.json()
    all_posts = []

    for post in posts_data['data']['children']:
        # Skip bot-generated or empty posts
        if not post['data'].get('title', '').strip() and not post['data'].get('selftext', '').strip():
            continue

        post_details = {
            "title": post['data'].get('title', ''),
            "body": post['data'].get('selftext', ''),
        }

        all_posts.append(post_details)

    return all_posts

# Save to file
def save_to_file(subreddit_name, posts, file_name):
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(f"Subreddit: {subreddit_name}\n\n")
        for idx, post in enumerate(posts):
            file.write(f"Post {idx + 1}:\n")
            file.write(f"Title: {post['title']}\n")
            file.write(f"Body: {post['body']}\n\n")
    print(f"Data saved to {file_name}")

# Main script
def main():
    subreddit_url = input("Enter the Reddit subreddit URL: ").strip()
    file_name = input("Enter the name of the output file (default: subreddit_data.txt): ").strip()
    if not file_name:
        file_name = "subreddit_data.txt"

    print("To fetch data, enter your Reddit API credentials. You can get these by registering a script on https://www.reddit.com/prefs/apps.")
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    user_agent = input("Enter your User-Agent string: ").strip()

    limit = input("Enter the number of latest posts to fetch: ").strip()
    if not limit.isdigit() or int(limit) <= 0:
        print("Invalid number of posts. Defaulting to 10.")
        limit = 10
    else:
        limit = int(limit)

    try:
        # Get Bearer token
        access_token = get_access_token(client_id, client_secret, user_agent)
        headers = {
            "User-Agent": user_agent,
            "Authorization": f"Bearer {access_token}"
        }

        subreddit_name = subreddit_url.rstrip('/').split('/')[-1]
        posts = fetch_subreddit_posts(subreddit_name, headers, limit)
        save_to_file(subreddit_name, posts, file_name)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
