from dotenv import load_dotenv
from chatui import ui

load_dotenv(override=True)


def main():
    ui.launch()


if __name__ == "__main__":
    main()
