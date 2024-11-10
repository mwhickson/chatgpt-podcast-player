from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Static

# Placeholder content
podcasts = ["Podcast 1", "Podcast 2", "Podcast 3"]
episodes = ["Episode 1", "Episode 2", "Episode 3"]

class PodcastPlayer(App):
    """A minimal TUI podcast player using Textual."""

    def compose(self) -> ComposeResult:
        # Header, main content (with podcasts and episodes), and footer
        yield Header()
        
        # Main content area with horizontal split for podcasts and episodes
        with Horizontal():
            yield Static("Podcasts", id="podcast-title")
            yield Static("\n".join(f"- {podcast}" for podcast in podcasts), id="podcast-list")
            yield Static("Episodes", id="episode-title")
            yield Static("\n".join(f"- {episode}" for episode in episodes), id="episode-list")
        
        # Footer with usage instructions
        yield Footer()

    def action_quit(self):
        """Action to quit the application."""
        self.exit()

# Run the application
if __name__ == "__main__":
    app = PodcastPlayer()
    app.run()
