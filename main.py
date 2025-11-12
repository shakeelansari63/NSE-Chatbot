from dotenv import load_dotenv

from chatui import ui

load_dotenv(override=True)


def main():
    ui.launch(server_port=8000, server_name="0.0.0.0")


if __name__ == "__main__":
    main()
