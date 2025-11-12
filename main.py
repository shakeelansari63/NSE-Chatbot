from dotenv import load_dotenv

load_dotenv(override=True)

from chatui import ui  # noqa # Dot Env needs to be loaded before reading any config


def main():
    ui.launch(server_port=8000, server_name="0.0.0.0")


if __name__ == "__main__":
    main()
