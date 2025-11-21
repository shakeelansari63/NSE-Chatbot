import gradio as gr
from gradio.themes.ocean import Ocean
from gradio.themes.utils import colors, fonts

app_theme = Ocean(
    primary_hue=colors.purple,
    secondary_hue=colors.blue,
    neutral_hue=colors.zinc,
    font=[fonts.GoogleFont("Ubuntu"), "Arial", "sans-serif"],
    font_mono=[fonts.GoogleFont("Ubuntu Mono"), "Arial", "sans-serif"],
)

app_css = """
/* Custom CSS for App */
footer {display:none !important};

.example-button {
    height: 100px;
    padding: 10px 20px;
}
"""
