import click
from rich.console import Console
from rich import print
from websocket import create_connection
import json
import pyfiglet

console = Console()
# Display ASCII art for Cerast Intelligence
ascii_art = pyfiglet.figlet_format("Cerast Intelligence")
console.print(f"[bold magenta]{ascii_art}[/bold magenta]")

class DataStreamMonitor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.is_connected = False

    def start(self):
        if not self.api_key:
            console.print("Please provide your API key to start monitoring.", style="bold red")
            return

        try:
            self.ws = create_connection(f"wss://stream.cerast-intelligence.com:8080/ws")
            self.ws.send(self.api_key)
            self.is_connected = True
            console.print("[bold green]Successfully connected to the data stream.[/bold green]")
            self.listen()
        except Exception as e:
            console.print(f"[bold red]An error occurred while connecting: {e}[/bold red]")
            self.is_connected = False

    def listen(self):
        try:
            while self.is_connected:
                result = self.ws.recv()
                if result:
                    self.handle_message(result)
        except Exception as e:
            console.print(f"[bold red]Error receiving data: {e}[/bold red]")
            self.is_connected = False

    def handle_message(self, message):
        try:
            message_json = json.loads(message)
            impact_color = {
                "LOW": "green",
                "MEDIUM": "yellow",
                "HIGH": "red"
            }

            domain = message_json.get("domain", "")
            path = message_json.get("path", "")
            category = message_json.get("category", "")
            if category =="exposed":
                category = "exposed filetree"
            impact = message_json.get("impact", "")

            console.print(f"[bold cyan]Domain:[/bold cyan] {domain} | "
                          f"[bold green]Path:[/bold green] {path} | "
                          f"[bold magenta]Category:[/bold magenta] {category} | "
                          f"[bold {impact_color.get(impact, 'white')}]Impact:[/bold {impact_color.get(impact, 'white')}] {impact}")

        except json.JSONDecodeError:
            console.print(f"[bold blue]New message received:[/bold blue] {message}")

@click.command()
@click.option('--api_key', prompt='Your API key', help='API key for accessing the data stream.')
def start_monitor(api_key):
    monitor = DataStreamMonitor(api_key)
    monitor.start()

if __name__ == "__main__":
    start_monitor()
