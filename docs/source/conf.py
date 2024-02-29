"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""

from __future__ import annotations

__copyright__ = "Copyright 2024, Molara"

project = "Molara"
project_copyright = "2023, Michel Heinz"
author = "Michel Heinz"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.todo", "sphinx.ext.autodoc", "sphinx.ext.autosummary", "myst_parser"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- General configuration ---------------------------------------------------
# grab the release, i.e. the full version, including alpha/beta/rc tags.
release = "0.0.1"
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
    'logo_only': False,      # only display the logo not the project name
    'display_version': True, # display the version number in the sidebar
}