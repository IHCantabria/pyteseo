# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
from pyteseo.__init__ import __version__


project = "pyTESEO"
copyright = "2022, Germán Aragón Caminero"
author = "Germán Aragón Caminero"
version = release = __version__

html_context = {
    "display_github": True,  # Integrate GitHub
    "github_user": "ihcantabria",  # Username
    "github_repo": "pyteseo",  # Repo name
    "github_version": "main",  # Version
    "conf_py_path": "/docs/",
}

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "autoapi.extension",
    "sphinx_rtd_theme",
    "myst_nb",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
    "style_external_links": False,
}
# html_theme = 'furo'
# html_theme = 'sphinx_book_theme'

html_static_path = ["_static"]
html_logo = "_static/pyTESEO_logo.png"
html_title = " v" + release

# -- Options for autoapi ext -------------------------------------------------

autoapi_modules = {"pyteseo": None}
autoapi_dirs = ["../pyteseo"]
autoapi_ignore = ["*/test_*.py"]
# autoapi_add_toctree_entry = False
