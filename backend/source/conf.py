import os
import sys
sys.path.insert(0, os.path.abspath("../backend"))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Policy Pal'
copyright = '2025, Alexander Edwards, Jacob Ryan, Tyler Cho, Akash Banerjee, Raphael Luis Santos,Armeen Seyed Makki'
author = 'Alexander Edwards, Jacob Ryan, Tyler Cho, Akash Banerjee, Raphael Luis Santos,Armeen Seyed Makki'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
