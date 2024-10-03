"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

from __future__ import annotations

from datetime import datetime, timezone

from molara import __version__

__copyright__ = f"Copyright {datetime.now(timezone.utc).year}, Molara"

project = "Molara"
project_copyright = f"2023\u2013{datetime.now(timezone.utc).year}, Molara Team"
author = "Michel Heinz"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- General configuration ---------------------------------------------------
# grab the release from the package's __init__.py file
release = __version__
# to distinguish X.Y version (assume PEP 440 compliant versioning) from release,
# uncomment the following:
# version = re.match(r"(\d+!)?(\d+\.\d+).*", release).group(2)
# Here, we use the full version as the version number:
version = release


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_logo = "_static/logo.png"
html_theme_options = {
    "logo_only": False,  # only display the logo not the project name
    "display_version": True,  # display the version number in the sidebar
}
