import requests
import feedparser
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button, ListView, ListItem
from textual.events import Key
from textual.widget import Widget
from textual.reactive import Reactive

class Podcast:
    def __init__(self, title, feed_url, description):
        self.title = title
        self.feed_url = feed_url
        self.description = description
        self.episodes = []

    def fetch_episodes(self):
        """Fetch episodes from the podcast feed."""
        feed = feedparser.parse(self.feed_url)
        self.episodes = [
            {
                "title": entry.title,
                "url": entry.enclosures[0].href if entry.enclosures else None,
                "description": entry.summary,
                "duration": entry.itunes_duration if "itunes_duration" in entry else "Unknown"
            }
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

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle podcast selection (either via mouse click or other selection)."""
        selected_item = event.item  # Get the selected item (ListItem)
        selected_podcast = selected_item.metadata  # Retrieve the podcast from metadata
        selected_podcast.fetch_episodes()  # Fetch episodes from the feed
        self.update_episode_list(selected_podcast.episodes)

    def update_episode_list(self, episodes):
        """Update the episode list in the UI with episodes of the selected podcast."""
        episode_list_view = self.query_one("#episode_list")
        episode_list_view.clear()
        for episode in episodes:
            episode_info = f"{episode['title']} - {episode['duration']}"
            item = ListItem(Static(episode_info))  # Use Static to display episode info
            item.metadata = episode
            episode_list_view.append(item)

# Run the application
if __name__ == "__main__":
    app = PodcastPlayer()
    app.run()
