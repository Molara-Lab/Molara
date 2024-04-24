"""Get colors table."""

from __future__ import annotations

import json

import bs4
import requests
from bs4 import BeautifulSoup

# from ase.data.colors import cpk_colors, jmol_colors

file_path = "../../src/molara/Structure/"


def fetch_color_table() -> bs4.element.Tag:
    """Fetch the color table from the wikipedia page."""
    url = "https://en.wikipedia.org/wiki/CPK_coloring"
    response = requests.get(url, timeout=5)
    soup = BeautifulSoup(response.text, "html.parser")

    table = None
    for table in soup.find_all("table", {"class": "wikitable"}):
        if "CPK coloring" in table.get_text():
            break
    assert table is not None, "Table not found."

    return table


def parse_color_table(table: bs4.element.Tag) -> dict[str, dict[str, str]]:
    """Parse the color table."""
    data = []
    for tr in table.find_all("tr"):
        row = []
        for td in tr.find_all("td"):
            if td:
                tag = td.find("span")
                if tag:
                    style_attribute = tag.get("style")
                    if style_attribute:
                        style_properties = style_attribute.split(";")
                        for prop in style_properties:
                            if "background-color" in prop:
                                background_color_value = prop.split(":")[1].strip()
                                row += [background_color_value]
                                break
                else:
                    row += [td.get_text().strip()]
        data += [row]

    data = data[2:]
    data = [[None if cell == "" else cell for cell in row] for row in data]

    colors_dict: dict[str, dict[str, str]] = {}
    for idx, scheme in enumerate(data[0]):
        colors_dict[str(scheme)] = {}
        for row in data[1:]:
            colors_dict[str(scheme)][str(row[1])] = str(row[idx + 3])

    return colors_dict


if __name__ == "__main__":
    c_table = fetch_color_table()
    colors_dict = parse_color_table(c_table)

    with open(file_path + "atom_colors.json", "w") as file:
        json.dump(colors_dict, file)
