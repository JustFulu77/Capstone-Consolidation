import os
import sys
import django

sys.path.insert(0, os.path.abspath('../..'))  # adjust to project root
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'  # replace Newsletter with your project name
django.setup()

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Fulu'
copyright = '2025, Fulu'
author = 'Fulu'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme =  'sphinx_rtd_theme'
html_static_path = ['_static']
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # for Google-style docstrings
]
