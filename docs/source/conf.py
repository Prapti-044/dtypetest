import os
import sys

sys.path.insert(0, os.path.abspath('../../'))

project = 'dtypetest'
copyright = '2024, Shadmaan Hye'
author = 'Shadmaan Hye'
release = '0.0.1'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx.ext.viewcode', 'sphinx.ext.autosummary']

autosummary_generate = True
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'special-members': True,
    'inherited-members': True,
}



templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
