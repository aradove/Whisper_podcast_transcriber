import feedparser
import requests
import whisper
import json
from pathlib import Path
from datetime import datetime
import shutil
import torch
import re

class PodcastsDB:
    """ 
    A class that uses a json file as a database to store what episodes has been downloaded and transcribed
    """
    def __init__(self, db_file='downloaded_episodes.json'):
        self.db_file = db_file
        self.downloaded_episodes = self.load_downloaded_episodes()

    def load_downloaded_episodes(self):
        """Load the downloaded episodes from the JSON file"""
        try:
            with open(self.db_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            # self.downloaded_episodes = [{'title': "dummy", 'transcribed': False}]
            return [{'title': "dummy", 'transcribed': False}]

    def is_episode_downloaded(self, episode_title):
        """Check if an episode is downloaded
        Args:
            episode_title (str): The title of the episode to mark as transcribed
        """
        return any(episode['title'] == episode_title for episode in self.downloaded_episodes)

    def is_episode_transcribed(self, episode_title):
        """Check if an episode is transcribed
        Args:
            episode_title (str): The title of the episode to mark as transcribed
        """
        return any(episode['title'] == episode_title and episode['transcribed'] for episode in self.downloaded_episodes)

    def add_downloaded_episode(self, episode_title):
        """Add an episode to the list of downloaded episodes
        Args:
            episode_title (str): The title of the episode to mark as transcribed
        """
        self.downloaded_episodes.append({'title': episode_title, 'transcribed': False})
        self.save_downloaded_episodes()

    def mark_episode_as_transcribed(self, episode_title):
        """Mark an episode as transcribed
        Args:
            episode_title (str): The title of the episode to mark as transcribed
        """
        for episode in self.downloaded_episodes:
            if episode['title'] == episode_title:
                episode['transcribed'] = True
                break
        self.save_downloaded_episodes()

    def save_downloaded_episodes(self):
        """Save the current state of the JSON file and create a backup"""
        with open(self.db_file, 'w') as file:
            json.dump(self.downloaded_episodes, file)

        # Create a backup of the JSON file
        backup_file = f"{self.db_file}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copy(self.db_file, backup_file)

        # Keep only the last 100 backup files
        db_file_relative = Path(self.db_file).relative_to(Path.cwd())
        backup_files = sorted(Path('.').glob(f"{db_file_relative}_*.bak"), key=lambda f: f.stat().st_mtime, reverse=True)
        for backup_file in backup_files[100:]:
            backup_file.unlink()    

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

# code to check for new episodes of podcast on apple podcasts, such as Kvalitetsaktiepodden
def check_all_episodes(podcast_rss):
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
    return episodes

def download_episode(db, episode_url, episode_title, file_name="latest_episode.mp3"):
    # Check if the episode is already downloaded
    if db.is_episode_downloaded(episode_title):
        print(f"Episode '{episode_title}' is already downloaded")
        return

    # Download the episode
    response = requests.get(episode_url)

    # Save the episode to a file
    with open(file_name, 'wb') as file:
        file.write(response.content)

    print(f"Episode from {episode_url} downloaded and saved to {file_name}")

    # Add the episode to the downloaded episodes
    db.add_downloaded_episode(episode_title)

def transcribe_episode(db, episode_title, file_name="latest_episode.mp3", output_folder="transcripts"):
    # Check if the episode is already transcribed
    if db.is_episode_transcribed(episode_title):
        print(f"Episode '{episode_title}' is already transcribed")
        return
    
    print("Loading whisper model")
    model = whisper.load_model("large-v3", device="cuda")
    print("Starting transcription...")
    result = model.transcribe(str(file_name), language="sv", verbose=False)

    # Create a new file name for the transcript
    transcript_file_name = episode_title + '.txt'

    # Write the transcribed text to a file
    output_folder_path = Path(output_folder)
    output_folder_path.mkdir(exist_ok=True)

    output_path = Path(output_folder) / transcript_file_name
    # file write with encoding utf-8
    with open(output_path, 'w', encoding="utf-8") as file:
        file.write(result["text"].replace(". ", ".\n"))

    print(f"Transcription saved to {output_path}")

    # Mark the episode as transcribed
    db.mark_episode_as_transcribed(episode_title)


def sanitize_filename(filename):
    # Remove invalid characters
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    
    # Remove leading/trailing whitespace
    filename = filename.strip()
    
    return filename

# Replace with the RSS feed which you can find at "https://castos.com/tools/find-podcast-rss-feed/"
podcast_rss = "https://feeds.acast.com/public/shows/60c356060f75f600192eac7f"
file_name = "Kvalitetsaktiepodden.mp3"

# Check for new episodes and download the latest one
latest_episode_url, latest_episode_title = check_new_episodes(podcast_rss)

# Create/load json database
database_folder = Path(__file__).parent / "db"
database_folder.mkdir(exist_ok=True)
database_path = Path(database_folder) / 'downloaded_episodes.json'
db = PodcastsDB(database_path)

# Download the episode
output_folder = Path(__file__).parent / "transcripts" / "kvalitetsaktiepodden"
mp3_file_path = output_folder / (sanitize_filename(latest_episode_title) + ".mp3")
download_episode(db, latest_episode_url, latest_episode_title, file_name=mp3_file_path)

# Transcribe the episode
transcription_file_path = output_folder / "kvalitetsaktiepodden"
transcribe_episode(db, latest_episode_title, file_name=mp3_file_path, output_folder=output_folder)


# Trascribe all episodes
episodes = check_all_episodes(podcast_rss)
for episode in episodes:
    latest_episode_url = episode.enclosures[0].href
    latest_episode_title = episode.title
    
    print(f"Downloading episode: {episode.title}")
    mp3_file_path = output_folder / (sanitize_filename(latest_episode_title) + ".mp3")
    download_episode(db, latest_episode_url, latest_episode_title, file_name=mp3_file_path)

    # Transcribe the episode
    transcribe_episode(db, latest_episode_title, file_name=mp3_file_path, output_folder=output_folder)


