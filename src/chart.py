"""Generate matplotlib representations of data."""

import pathlib
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.units as munits

# Have matplotlib use a concise formatter for time-based data
converter = mdates.ConciseDateConverter()
munits.registry[np.datetime64] = converter
munits.registry[datetime.date] = converter
munits.registry[datetime.datetime] = converter


def generate_scatter_plot_single_category(
    chart_title: str,
    filename: pathlib.Path,
    chart_legend: str,
    color: str,
    y_data: list,
) -> None:
    """Generate scatter plot, where each point is a post.

    PARAMETERS
        filename: Filepath to save the resulting chart.
        chart_legend: the name that appears for that category on the legend.
        color: the color to be displayed on chart for that category.
        y_data: tally of the post's tags matching a given custom category.
        x data is calculated inside this function.
    """
    fig, ax = plt.subplots()
    # A dark grey
    # ax.set_facecolor("#4c6185")
    # A light grey
    # ax.set_facecolor("#adbed9")
    # a dark white
    # ax.set_facecolor("#bacae3")
    # A light white
    ax.set_facecolor("#deeafc")
    ax.set_title(chart_title)
    ax.set_xlabel("Percentile")
    ax.set_ylabel("Relevancy")

    # Default size is 6.4 x 4.8
    # fig.set_size_inches(10, 10)

    # Sort y data
    y = sorted(y_data, reverse=False)

    # We set the x data to step go from 0 to 100, across len(y_data) steps.
    # This way, the chart can be used to easily discern observations such as
    # "75% of posts have 10 or more tags relevant to (Custom Category))."
    x = []
    step_size = len(y) / 100
    # Set the x data to space the points out uniformly
    for i in range(0, len(y), 1):
        x.append(i / step_size)

    ax.scatter(x, y, c=color, label=chart_legend, alpha=0.5, edgecolors="none")

    ax.legend(loc="upper right")
    ax.grid(True)

    # fig.tight_layout()
    fig.savefig(filename, facecolor="#adbed9", bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def generate_scatter_plot_post_score(
    chart_title: str, filename: pathlib.Path, x_data, y_data: list, x_label: str
) -> None:
    """Generate scatter plot, where each point is a post.

    PARAMETERS
        x_data: post upload date
        y_data: post score
    """
    fig, ax = plt.subplots()
    # A dark grey
    # ax.set_facecolor("#4c6185")
    # A light grey
    # ax.set_facecolor("#adbed9")
    # a dark white
    # ax.set_facecolor("#bacae3")
    # A light white
    ax.set_facecolor("#deeafc")
    ax.set_title(chart_title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Score")

    # Default size is 6.4 x 4.8
    # fig.set_size_inches(10, 10)

    ax.scatter(x_data, y_data, c="tab:blue", alpha=0.5, edgecolors="none")

    # ax.legend(loc="upper right")
    ax.grid(True)

    # fig.tight_layout()
    fig.savefig(filename, facecolor="#adbed9", bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def generate_bar_chart(
    chart_title: str, filename: pathlib.Path, data: dict[str, int]
) -> None:
    """Generate bar chart, where each bar is a tag.

    PARAMETERS
        filename: Filepath to save the resulting chart.
        Data: each bar is an element of data,
         key = name
         value = bar length
    """
    fig, ax = plt.subplots()
    ax.set_facecolor("#deeafc")
    ax.set_title(chart_title)
    ax.set_xlabel("Tag")
    ax.set_ylabel("% of Posts")

    width = 0.6
    bar_container = ax.bar(data.keys(), data.values(), width)
    ax.bar_label(bar_container, labels=data.keys(), label_type="edge", rotation=45.0)

    # remove x-axis labels
    ax.set_xticklabels([])
    ax.set_yticks(np.arange(0.0, 1.01, 0.2))

    # fig.tight_layout()
    fig.savefig(filename, facecolor="#adbed9", bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def generate_scatter_plot_all_custom_categories(
    chart_title: str,
    filename: pathlib.Path,
    category_to_chart_legend: dict,
    category_to_color: dict,
    category_to_y_data: dict,
    x_data: list,
) -> None:
    """Generate scatter plot, where each point is a post (multiple categories).

    PARAMETERS
        filename: Filepath to save the resulting chart.
        category_to_chart_legend: maps category to the legend string.
          We plot the categories in the same order as they appear in the legend map.
        category_to_color: maps category to it's color on the chart.
        category_to_data: maps category to the dict of "x" and "y" datapoints.
         Each datapoint is a single post.
         y = tally of general tags in a given m2 category.
         x = post upload date.
    """
    fig, ax = plt.subplots()
    # A dark grey
    # ax.set_facecolor("#4c6185")
    # A light grey
    # ax.set_facecolor("#adbed9")
    # a dark white
    # ax.set_facecolor("#bacae3")
    # A light white
    ax.set_facecolor("#deeafc")
    ax.set_title(chart_title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Relevancy")

    # Default size is 6.4 x 4.8
    # fig.set_size_inches(10, 10)

    for category in category_to_chart_legend.keys():
        x = x_data
        y = category_to_y_data[category]
        ax.scatter(
            x,
            y,
            c=category_to_color[category],
            label=category_to_chart_legend[category],
            alpha=0.5,
            edgecolors="none",
        )
        # ax.set_title(chart_title)

    ax.legend(loc="upper right")
    ax.grid(True)

    # fig.tight_layout()
    fig.savefig(filename, facecolor="#adbed9", bbox_inches="tight", pad_inches=0)
    plt.close(fig)
