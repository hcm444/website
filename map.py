import sqlite3
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import matplotlib.colors as mcolors  # Added import for fading colors


def fade_color(base_color, opacity):
    rgba = mcolors.colorConverter.to_rgba(base_color)
    faded_rgba = rgba[:3] + (opacity,)
    return faded_rgba


def map_data(shapefile_path, filename, database):
    if os.path.exists(f"static/maps/{filename}.png"):
        os.remove(f"static/maps/{filename}.png")

    conn = sqlite3.connect(database)
    data = pd.read_sql_query(
        "SELECT icao24, latitude, longitude, timestamp, callsign FROM flights ORDER BY timestamp LIMIT 180", conn
    )

    shapefile = gpd.read_file(shapefile_path)
    groups = data.groupby("icao24")

    fig, ax = plt.subplots(figsize=(12, 12))
    fig.patch.set_facecolor('none')  # Set the figure background to transparent
    ax.set_facecolor('none')  # Set the axes background to transparent
    shapefile.plot(ax=ax, alpha=1, facecolor='none', edgecolor='green')
    xmin, ymin, xmax, ymax = shapefile.total_bounds
    patch = plt.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, fill=True, facecolor='black', zorder=-1)
    ax.add_patch(patch)
    ax.set_axis_off()

    for idx, (name, group) in enumerate(groups):
        opacity = (idx + 1) / len(groups)
        line_color = fade_color('white', opacity)
        ax.plot(group["longitude"], group["latitude"], color=line_color, linewidth=1)

        if not pd.isna(group.iloc[0]["callsign"]):
            ax.text(group.iloc[0]["longitude"], group.iloc[0]["latitude"],
                    f"{name}\n{group.iloc[0]['callsign']}", color='white')
        else:
            ax.text(group.iloc[0]["longitude"], group.iloc[0]["latitude"],
                    f"{name}\n(no callsign)", color='white')

    plt.savefig(f"static/maps/{filename}.png", bbox_inches='tight', transparent=True)
    plt.close(fig)

    conn.close()

