# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import sphinx_material

from datetime import datetime

sys.path.insert(0, os.path.abspath('../..'))
from remo import __version__

# -- Project information -----------------------------------------------------

project = 'Remo SDK'
copyright = '{}, Rediscovery.io'.format(datetime.utcnow().year)
author = 'Rediscovery.io'

# The full version, including alpha/beta/rc tags
release = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

extensions = [
    'sphinx.ext.autodoc',
    # 'sphinx.ext.doctest',
    # 'sphinx.ext.todo',
    # 'sphinx.ext.coverage',
    # 'sphinx.ext.imgmath',
    # 'sphinx.ext.ifconfig',
    'sphinxcontrib.napoleon',
    # 'sphinx_markdown_builder'
]

# autosummary_generate = True
# autoclass_content = "class"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build/*']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
html_static_path = ["_static"]


# -- HTML theme settings ------------------------------------------------

extensions.append('sphinx_material')
html_theme = 'sphinx_material'
html_theme_path = sphinx_material.html_theme_path()

# See https://github.com/bashtage/sphinx-material/blob/master/docs/conf.py

html_theme_options = {

    # Set the name of the project to appear in the navigation.
    'nav_title': 'Remo SDK',

    # Set you GA account ID to enable tracking
    # 'google_analytics_account': 'UA-XXXXX',

    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    'base_url': 'https://rediscovery-io.github.io/remo-python-doc/',

    # Set the color and the accent color
    'color_primary': 'green',
    'color_accent': 'light-green',

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/rediscovery-io/remo-python',
    'repo_name': 'remo-python',

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 3,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,
}

html_context = sphinx_material.get_html_context()
