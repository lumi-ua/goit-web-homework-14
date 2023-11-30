import sys
import os
sys.path.insert(0, os.path.abspath('..'))
project = 'Contacts Rest App'
copyright = '2023, lumi-ua'
author = 'lumi-ua'


autodoc_mock_imports = ['pydantic_settings']

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


html_theme = 'nature'
html_static_path = ['_static']

