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

/* Force chatbot block border to 0 width so inline border-style: solid is invisible */
#nse-chatbot {
    border: 0 none !important;
    border-width: 0 !important;
    border-style: none !important;
    box-shadow: none !important;
}
/* Also zero out the CSS variable on the styler parent */
div.styler:has(#nse-chatbot) {
    --block-border-width: 0 !important;
}
gradio-group {
    border: none !important;
    box-shadow: none !important;
}
"""
