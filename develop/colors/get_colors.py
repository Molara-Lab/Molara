"""Get the colors for the atoms from the wikipedia page and store them in a json file.

The colors are fetched from the wikipedia page: https://en.wikipedia.org/wiki/CPK_coloring. Additionally, the colors
 from the ASE package are included. This is a developer script to generate the atom_colors.json file.
"""

from __future__ import annotations

import json
from pathlib import Path

import bs4
import requests
from ase.data.colors import cpk_colors, jmol_colors  # pylint: ignore[reportMissingImports]
from bs4 import BeautifulSoup

from molara.structure.atom import atomic_number_to_symbol

file_path = Path(__file__).parent.parent.parent / "src" / "molara" / "structure"


def fetch_color_table() -> bs4.element.Tag:
    """Fetch the color table from the wikipedia page."""
    url = "https://en.wikipedia.org/wiki/CPK_coloring"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36",
    }
    response = requests.get(url, headers=headers, timeout=5)
    soup = BeautifulSoup(response.text, "html.parser")

    table = None
    for table in soup.find_all("table", {"class": "wikitable"}):
        if "CPK coloring" in table.get_text():
            break
    assert table is not None, "Table not found."

    return table


def parse_color_table(table: bs4.element.Tag) -> dict[str, dict[str, str]]:  # noqa: C901, PLR0912
    """Parse the color table from the wikipedia page."""
    data = []
    # Process both header (th) and data cells (td)
    for tr in table.find_all("tr"):
        row = []
        for cell in tr.find_all(["td", "th"]):
            bg_color = None
            # Search for style attributes in the cell itself OR in child tags (like span)
            elements_to_check = [cell, *cell.find_all(name=True)]
            for el in elements_to_check:
                style = el.get("style", "")
                if "background-color" in style:
                    # Extrahiere die Farbe aus dem Style-String
                    for prop in style.split(";"):
                        if "background-color" in prop:
                            bg_color = prop.split(":")[1].strip()
                            break
                if bg_color:
                    break
            if bg_color:
                row.append(bg_color)
            else:
                text = cell.get_text().strip()
                row.append(text if text != "" else None)
        if row:
            data.append(row)

    data = data[2:]

    colors_dict: dict[str, dict[str, str]] = {}

    headers = data[0][3:]

    for offset, scheme_name in enumerate(headers):
        if not scheme_name:
            continue

        col_idx = offset + 3
        colors_dict[scheme_name] = {}
        for row in data[1:]:
            symbol = row[1]
            color = row[col_idx]
            if color is not None:
                colors_dict[scheme_name][symbol] = color

    return colors_dict


def get_ase_colors() -> dict[str, dict[str, tuple]]:
    """Get the ASE colors."""
    ase_colors: dict[str, dict[str, tuple]] = {}
    for scheme_name, values in {"Jmol_ase": jmol_colors, "CPK_ase": cpk_colors}.items():
        ase_colors[scheme_name] = {}
        ase_colors[scheme_name]["None"] = tuple(values[0])
        for atomic_number in range(1, len(values)):
            ase_colors[scheme_name][atomic_number_to_symbol(atomic_number)] = tuple(values[atomic_number])

    return ase_colors


if __name__ == "__main__":
    c_table = fetch_color_table()

    with (Path(file_path) / "atom_colors.json").open("w", encoding="utf-8") as file:
        json.dump(parse_color_table(c_table) | get_ase_colors(), file)
