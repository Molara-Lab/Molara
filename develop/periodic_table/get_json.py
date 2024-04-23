"""Get the periotic table data from pymatgen and save it to a file."""

from __future__ import annotations

import json
import urllib.request

file_path = "../../src/molara/Structure/"

with urllib.request.urlopen(
    "https://raw.githubusercontent.com/materialsproject/pymatgen/master/pymatgen/core/periodic_table.json",
) as url:
    data = json.load(url)

with open(file_path + "periodic_table.json", mode="w") as file:
    json.dump(data, file)

with urllib.request.urlopen(
    "https://raw.githubusercontent.com/materialsproject/pymatgen/master/LICENSE",
) as url:
    license_text = url.read().decode("utf-8")

with open(file_path + "periodic_table_copyright.txt", mode="w") as file:
    file.write("Periodic Table data from pymatgen.\nThe data is licensed under the following terms.\n\n")
    file.write(license_text)
