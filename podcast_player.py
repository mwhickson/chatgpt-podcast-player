from datetime import timedelta
import pygame
import requests
import feedparser
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, Input, Button, ListView, ListItem, ProgressBar
from textual.events import Key
from textual.widget import Widget
from textual.reactive import Reactive
from textual.screen import Screen
from pygame import mixer
import time
import os
import tempfile
import concurrent.futures

# Episode class with audio_url
class Episode:
    def __init__(self, title, description, duration, audio_url):
        self.title = title
        self.description = description
        # Make sure the duration is a valid number (if not, set to 0.0 or some default value)
        try:
            self.duration = float(duration) if duration and duration != "Unknown" else 0.0
        except ValueError:
            self.duration = 0.0  # Default to 0.0 if invalid
        self.audio_url = audio_url

class Podcast:
    """Class to represent a podcast."""
    
    def __init__(self, title, feed_url, description):
        self.title = title
        self.feed_url = feed_url
        self.description = description
        self.episodes = []

    def fetch_episodes(self):
        """Fetch episodes from the podcast feed."""
        feed = feedparser.parse(self.feed_url)
        self.episodes = [
            Episode(
                entry.title,
                entry.summary,
                entry.itunes_duration if "itunes_duration" in entry else "Unknown",
                entry.enclosures[0].href if entry.enclosures else None
            )
            for entry in feed.entries
        ]

def search_podcasts(term):
    """Search for podcasts by term using the iTunes API."""
    url = "https://itunes.apple.com/search"
    params = {
        "term": term,
        "media": "podcast",
        "entity": "podcast"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json().get("results", [])

    podcasts = []
    for result in results:
        title = result.get("collectionName")
        feed_url = result.get("feedUrl")
        description = result.get("description") or result.get("collectionName", "")
        
        if title and feed_url:
            podcasts.append(Podcast(title, feed_url, description))

    return podcasts

class EpisodeDetailScreen(Screen):
    """Screen to display episode details and allow playback controls."""

    def __init__(self, episode):
        super().__init__()
        self.episode = episode
        self.is_playing = False
        self.is_paused = False
        self.current_time = 0  # Start at the beginning of the episode
        self.audio = None  # Placeholder for the audio file

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

    def compose(self) -> ComposeResult:
        """Compose the elements of the screen."""
        # Episode title, duration, and description
        yield Static(f"Title: {self.episode.title}")
        yield Static(f"Duration: {self.episode.duration}")
        yield Static(f"Description: {self.episode.description}")

        # Add Play Episode button
        yield Button("Play Episode", id="play_button")

        # Add Back to Podcast button
        yield Button("Back to Podcast", id="back_button")

        # Progress bar to show current progress
        #progress_bar = ProgressBar(total=100, id="progress_bar", show_percentage=True)
        #yield progress_bar

        # Timestamp display (Current Position)
        #yield Static(f"Current Position: {self.format_time(self.current_time)}", id="timestamp")

        # Play/Pause button
        yield Button("Play/Pause", id="play_pause_button")

    def on_button_pressed(self, event) -> None:
        """Handle button press events in the episode detail screen."""
        if event.button.id == "play_button":
            self.start_playing()
        elif event.button.id == "play_pause_button":
            self.toggle_play_pause()
        elif event.button.id == "back_button":
            self.app.pop_screen()  # Go back to the podcast list screen

    def toggle_play_pause(self) -> None:
        """Toggle between playing and paused states."""
        if self.is_playing:
            pygame.mixer.music.pause()  # Pause the music
            self.is_playing = False
            self.is_paused = True
        elif self.is_paused:
            pygame.mixer.music.unpause()  # Unpause the music
            self.is_paused = False
            self.is_playing = True
            #self.update_progress_bar()

    def load_audio(self) -> None:
        """Download and load the audio file in a separate thread."""
        if not self.episode.audio_url:
            raise ValueError("No audio URL provided for the episode.")
        
        # Use ThreadPoolExecutor to download the audio file in the background
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.download_audio, self.episode.audio_url)
            future.add_done_callback(self.on_audio_download_complete)

    def download_audio(self, url: str):
        """Download the audio file and save it temporarily."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Check for HTTP errors
            
            # Save the audio file to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(response.content)
                temp_file.close()  # Close the file to allow pygame to access it
                return temp_file.name  # Return the path to the temporary file
        except requests.RequestException as e:
            print(f"Error downloading the episode: {e}")
            return None

    def on_audio_download_complete(self, future):
        """Handle the completion of the audio download."""
        audio_file = future.result()  # Get the result from the background thread
        if audio_file:
            self.audio = audio_file
            pygame.mixer.music.load(self.audio)
            self.start_playing()  # Start playing once the audio is loaded
        else:
            print("Failed to download the audio file.")

    def start_playing(self) -> None:
        """Start playing the episode."""
        if not self.audio:
            self.load_audio()
        if not self.is_playing:
            pygame.mixer.music.play(start=self.current_time)  # Start the music from the current time
            self.is_playing = True
            #self.update_progress_bar()

##    def update_progress_bar(self) -> None:
##        """Update the progress bar to reflect the current progress."""
##        if self.is_playing:
##            # Get the current position of the audio
##            self.current_time = pygame.mixer.music.get_pos() / 1000  # Convert ms to seconds
##            if self.current_time >= self.episode.duration:
##                self.is_playing = False  # Stop when the episode finishes
##            self.update_ui()
##
##        # Directly call the method in call_later without using partial
##        #self.call_later(1, self.update_progress_bar)
##    
##    def update_ui(self) -> None:
##        """Update the UI elements to reflect current time and progress."""
##        progress_bar = self.query_one("#progress_bar")
##        
##        if self.episode.duration > 0:  # Prevent division by zero
##            progress_bar.value = (self.current_time / self.episode.duration) * 100
##        else:
##            progress_bar.value = 0  # Set to 0% if the duration is zero
##
##        self.query_one("#timestamp").update(f"Current Position: {self.format_time(self.current_time)}")
##
##    def format_time(self, seconds: int) -> str:
##        """Convert seconds to a readable timestamp format."""
##        return str(timedelta(seconds=seconds))
##
##    def on_progress_bar_clicked(self, event: events.Click) -> None:
##        """Handle progress bar click to seek within the episode."""
##        # Calculate the clicked position as a percentage of the total duration
##        progress_bar = self.query_one("#progress_bar")
##        clicked_position = event.x / progress_bar.size.width
##        self.current_time = int(clicked_position * self.episode.duration)
##        pygame.mixer.music.play(start=self.current_time)  # Start playback from the clicked position
##        self.update_ui()  # Update the UI to reflect the new position
##
##    def on_music_finished(self):
##        """Callback when music finishes playing."""
##        self.is_playing = False
##        pygame.mixer.music.stop()
##        if self.audio:
##            os.remove(self.audio)  # Delete the temporary audio file when done
##            self.audio = None

class PodcastPlayer(App):
    """A TUI Podcast Player using Textual with iTunes API integration."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Input(placeholder="Enter a search term...", id="search_input")
            yield Button("Search", id="search_button")
            with Horizontal():
                yield ListView(id="podcast_list")
                yield ListView(id="episode_list")
        yield Footer()

    async def on_mount(self):
        """Initialize data and set up listeners."""
        self.podcast_list = []
        self.episodes = []

    async def on_button_pressed(self, event):
        """Handle search button click to search for podcasts."""
        if event.button.id == "search_button":
            search_term = self.query_one("#search_input").value.strip()
            if search_term:
                self.podcast_list = search_podcasts(search_term)
                self.update_podcast_list()

    def update_podcast_list(self):
        """Update the podcast list in the UI with search results."""
        podcast_list_view = self.query_one("#podcast_list")
        podcast_list_view.clear()
        for podcast in self.podcast_list:
            item = ListItem(Static(podcast.title))  # Use Static to display the podcast title
            item.metadata = podcast  # Store podcast data in metadata for later access
            podcast_list_view.append(item)

    async def on_list_view_selected(self, event) -> None:
        """Handle selection of podcasts or episodes."""
        selected_item = event.item  # Get the selected item (ListItem)
        selected_content = selected_item.metadata  # Retrieve metadata (either Podcast or Episode)

        # Check if the selected item is a Podcast
        if isinstance(selected_content, Podcast):
            selected_podcast = selected_content
            selected_podcast.fetch_episodes()  # Fetch episodes from the podcast feed
            self.update_episode_list(selected_podcast.episodes)

        # Check if the selected item is an Episode
        elif isinstance(selected_content, Episode):
            selected_episode = selected_content
            episode_screen = EpisodeDetailScreen(selected_episode)  # Create a new screen for episode details
            await self.push_screen(episode_screen)  # Push the episode detail screen

    def update_episode_list(self, episodes):
        """Update the episode list in the UI with episodes of the selected podcast."""
        episode_list_view = self.query_one("#episode_list")
        episode_list_view.clear()
        for episode in episodes:
            item = ListItem(Static(episode.title))  # Display episode title
            item.metadata = episode  # Store episode data in metadata
            episode_list_view.append(item)

    async def on_pop_screen(self, screen: Screen) -> None:
        """Handle returning to the main screen after episode detail view."""
        if isinstance(screen, EpisodeDetailScreen):
            # Re-initialize event handlers and refresh the podcast list after returning
            self.update_podcast_list()

# Run the application
if __name__ == "__main__":
    app = PodcastPlayer()
    app.run()
