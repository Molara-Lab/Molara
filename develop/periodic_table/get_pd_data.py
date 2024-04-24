"""Get the periotic table data from pymatgen and save it to a file."""

from __future__ import annotations

import json
import urllib.request

file_path = "../../src/molara/Structure/"

def fetch_periodic_table() -> dict[str, dict[str, str]]:
    """Fetch the periodic table data from pymatgen."""
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/materialsproject/pymatgen/master/pymatgen/core/periodic_table.json",
    ) as url:
        return json.load(url)

def fetch_license() -> str:
    """Fetch the license text from the pymatgen repository."""
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/materialsproject/pymatgen/master/LICENSE",
    ) as url:
        return url.read().decode("utf-8")

if __name__ == "__main__":

    pt_data = fetch_periodic_table()
    with open(file_path + "periodic_table.json", mode="w") as file:
        json.dump(pt_data, file)

    license_text = fetch_license()
    with open(file_path + "periodic_table_copyright", mode="w") as file:
        file.write("Periodic Table data from pymatgen.\nThe data is licensed under the following terms:\n\n")
        file.write(license_text)
