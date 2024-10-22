"""Get the colors for the atoms from the wikipedia page and store them in a json file.

The colors are fetched from the wikipedia page: https://en.wikipedia.org/wiki/CPK_coloring. Additionally, the colors
 from the ASE package are included. This is a developer script to generate the atom_colors.json file.
"""

from __future__ import annotations

import json

import bs4
import requests
from ase.data.colors import (
    cpk_colors,
    jmol_colors,
)  # pylint: ignore[reportMissingImports]
from bs4 import BeautifulSoup

from molara.structure.atom import atomic_number_to_symbol

file_path = "../../src/molara/structure/"


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


def get_ase_colors() -> dict[str, dict[str, tuple]]:
    """Get the ASE colors."""
    ase_colors: dict[str, dict[str, tuple]] = {}
    for scheme_name, values in {"Jmol_ase": jmol_colors, "CPK_ase": cpk_colors}.items():
        ase_colors[scheme_name] = {}
        ase_colors[scheme_name]["None"] = tuple(values[0])
        for atomic_number in range(1, len(values)):
            ase_colors[scheme_name][atomic_number_to_symbol(atomic_number)] = tuple(
                values[atomic_number],
            )

    return ase_colors


if __name__ == "__main__":
    c_table = fetch_color_table()

    with open(file_path + "atom_colors.json", "w") as file:
        json.dump(parse_color_table(c_table) | get_ase_colors(), file)
