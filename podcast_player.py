import requests
import feedparser
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button, ListView, ListItem
from textual.events import Key
from textual.widget import Widget
from textual.reactive import Reactive
from textual.screen import Screen

class Episode:
    """Class to represent a podcast episode."""
    
    def __init__(self, title, url, description, duration):
        self.title = title
        self.url = url
        self.description = description
        self.duration = duration

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
                entry.enclosures[0].href if entry.enclosures else None,
                entry.summary,
                entry.itunes_duration if "itunes_duration" in entry else "Unknown"
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
    """Screen to display episode details in a modal-like manner."""

    def __init__(self, episode):
        super().__init__()
        self.episode = episode

    def compose(self) -> ComposeResult:
        """Compose the elements of the screen."""
        yield Static(f"Title: {self.episode.title}")
        yield Static(f"Duration: {self.episode.duration}")
        yield Static(f"Description: {self.episode.description}")
        yield Button("Back to Podcast", id="back_button")

    async def on_button_pressed(self, event) -> None:
        """Handle button press events in the episode detail screen."""
        if event.button.id == "back_button":
            await self.app.pop_screen()  # Go back to the podcast list

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
            episode_info = f"{episode.title} - {episode.duration}"
            item = ListItem(Static(episode_info))  # Use Static to display episode info
            item.metadata = episode  # Store episode data in metadata for later access
            episode_list_view.append(item)

# Run the application
if __name__ == "__main__":
    app = PodcastPlayer()
    app.run()
