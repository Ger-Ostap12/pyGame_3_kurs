# Configuration file for the Sphinx documentation builder.

project = 'Asteroids Game'
copyright = '2025, PROJECTX'
author = '6 Щенят'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'sphinx_rtd_theme'  # Красивая тема (установи pip install sphinx-rtd-theme)
html_static_path = ['_static']

# Пути к исходникам (относительно docs)
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': True,
    'show-inheritance': True,
}

# Добавь sys.path для импорта модулей
import os
import sys
sys.path.insert(0, os.path.abspath('..'))  # Корень проекта