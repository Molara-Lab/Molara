"""Get the periotic table data from pymatgen and save it to a file.

The periodic table data is fetched from the pymatgen repository and saved to a file. This is a developer script to
 generate the periodic_table.json file.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

MODULE_DIR = Path(__file__).parent
PKG_DIR = Path(MODULE_DIR).parent
ROOT = (PKG_DIR).parent

file_path = ROOT / "src/molara/structure/"


def fetch_periodic_table() -> dict[str, dict[str, str]]:
    """Fetch the periodic table data from pymatgen."""
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/materialsproject/pymatgen/refs/heads/master/src/pymatgen/core/periodic_table.json",
    ) as url:
        return json.load(url)


def fetch_license() -> str:
    """Fetch the license text from the pymatgen repository."""
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/materialsproject/pymatgen/refs/heads/master/LICENSE",
    ) as url:
        return url.read().decode("utf-8")


if __name__ == "__main__":
    pt_data = fetch_periodic_table()
    with (file_path / "periodic_table.json").open(mode="w") as file:
        json.dump(pt_data, file)

    license_text = fetch_license()
    with (file_path / "periodic_table_copyright").open(mode="w") as file:
        file.write("Periodic Table data from pymatgen.\nThe data is licensed under the following terms:\n\n")
        file.write(license_text)
