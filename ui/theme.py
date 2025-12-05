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
/* Include Font Awesome CSS */
@import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css");

/* Custom CSS for App */
a {
    color: inherit;
    text-decoration: none;
}

/* Hide default Gradio Footer */
footer {display:none !important};
"""
