
import os

from dotenv import load_dotenv

from src.golems.document_editor import GolemDocumentEditor
from src.golems.golem import Golem

load_dotenv()



from rich.console import Console
console = Console()


class GolemGarden:
    def __init__(self):

        self._golem = Golem()

        # self._golem = GolemDocumentEditor()
    def run(self):
        console.print(f"[bold cyan] {self._golem.intake_message('A human is here and said Hello')}")

        while True:
            message = input("Enter message (or `quit`): ")
            if message == "quit":
                break
            console.print(self._golem.intake_message(message))

def main():
    console.rule("Welcome to Golem Garden 🌱", style="bold green")
    golem_garden = GolemGarden()
    golem_garden.run()


if __name__ == "__main__":
    main()