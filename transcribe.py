import feedparser
import requests
import whisper
import json
from pathlib import Path

# code to check for new episodes of podcast on apple podcasts, such as Kvalitetsaktiepodden
def check_new_episodes(podcast_rss):
    """
    Check for new episodes of a podcast
    # Find rss from "https://castos.com/tools/find-podcast-rss-feed/"

    Args:
        podcast_rss (str): The RSS feed of the podcast
                           Example: "https://feeds.acast.com/public/shows/60c356060f75f600192eac7f"

    Returns:
        latest_episode_url (str): The URL of the latest episode
        latest_episode_title (str): The title of the latest episode
    """
    # Parse the RSS feed
    feed = feedparser.parse(podcast_rss)

    # Get the list of episodes
    episodes = feed.entries

    # Get the URL and title of the latest episode
    latest_episode_url = episodes[0].enclosures[0].href
    latest_episode_title = episodes[0].title

    print("Latest episode: ", episodes[0].title)

    # Return the URL and title of the latest episode
    return latest_episode_url, latest_episode_title


def download_episode(episode_url, episode_title, file_name="latest_episode.mp3"):
    # Load the downloaded episodes from the JSON file
    try:
        with open('downloaded_episodes.json', 'r') as file:
            downloaded_episodes = json.load(file)
    except FileNotFoundError:
        downloaded_episodes = []
    
    # Check if the episode is already downloaded
    if episode_title in downloaded_episodes:
        print(f"Episode '{episode_title}' is already downloaded")
        return

    # Download the episode
    response = requests.get(episode_url)

    # Save the episode to a file
    with open(file_name, 'wb') as file:
        file.write(response.content)

    print(f"Episode from {episode_url} downloaded and saved to {file_name}")

    # Add the episode to the downloaded episodes
    downloaded_episodes.append(episode_title)

    # Save the downloaded episodes to the JSON file
    with open('downloaded_episodes.json', 'w') as file:
        json.dump(downloaded_episodes, file)

def transcribe_episode(episode_title, file_name="latest_episode.mp3", output_folder="transcripts"):
    model = whisper.load_model("base", device="cuda")
    result = model.transcribe(file_name)

    # Create a new file name for the transcript
    transcript_file_name = episode_title + '.txt'

    # Write the transcribed text to a file
    output_folder_path = Path(output_folder)
    output_folder_path.mkdir(exist_ok=True)

    output_path = Path(output_folder) / transcript_file_name
    with open(output_path, 'w') as file:
        file.write(result["text"])

    print(f"Transcription saved to {output_path}")


# Replace with the RSS feed which you can find at "https://castos.com/tools/find-podcast-rss-feed/"
podcast_rss = "https://feeds.acast.com/public/shows/60c356060f75f600192eac7f"
file_name = "Kvalitetsaktiepodden.mp3"

# Check for new episodes and download the latest one
latest_episode_url, latest_episode_title = check_new_episodes(podcast_rss)
download_episode(latest_episode_url, latest_episode_title, file_name)

# Transcribe the episode
transcribe_episode(latest_episode_title, file_name=file_name)