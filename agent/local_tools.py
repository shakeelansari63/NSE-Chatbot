import os
from tempfile import NamedTemporaryFile

import matplotlib.pyplot as plt
import seaborn as sns
from langchain.tools import tool

from server_config import get_server_config as sc


@tool
def get_line_chart_for_data(
    data: list[tuple[str, float]], title: str, x_label: str, y_label: str
) -> str:
    """
    Generates a Line Chart with given data. Input Data is a list of tuple which has 2 elements.
    The First element is X Axis value and the second element is Y Axis value.
    This function returns an markdown image tag with chart image url which can be embedded as is it in the response without any processing.
    """
    plt.figure(figsize=(12, 6))
    fig = sns.lineplot(x=[x for x, _ in data], y=[y for _, y in data])
    fig.set_title(title)
    fig.set_xlabel(x_label, loc="right")
    fig.set_ylabel(y_label)
    fig.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    with NamedTemporaryFile(
        dir=sc().temp_assets_url,
        suffix=".png",
        delete=False,
    ) as img:
        fig.get_figure().savefig(img, format="png")

        # File Url
        asset_url = f"/{sc().temp_assets_dir}/{os.path.basename(img.name)}"
        return f"![{title}]({asset_url})"
