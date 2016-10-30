#!/usr/bin/env python3
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinxcontrib.asyncio',
    'sphinxcontrib.httpdomain',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'AIO Consul'
copyright = '2016, AIO Consul'
author = 'AIO Consul'

version = '0.7.0'
release = '0.7.0'

language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'

todo_include_todos = False

# html_theme = 'alabaster'
html_theme = 'irrational'
html_theme_options = {
    'logo': 'logo.png',
    'description': "async/await client for the Consul HTTP API",
}
html_static_path = ['_static']
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}
htmlhelp_basename = 'AIOConsuldoc'
latex_elements = {
}
latex_documents = [
    (master_doc, 'AIOConsul.tex', 'AIO Consul Documentation',
     'AIO Consul', 'manual'),
]

man_pages = [
    (master_doc, 'aioconsul', 'AIO Consul Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'AIOConsul', 'AIO Consul Documentation',
     author, 'AIOConsul', 'One line description of project.',
     'Miscellaneous'),
]

autodoc_member_order = 'bysource'
autodoc_default_flags = ['members', 'undoc-members', 'inherited-members']
