#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PySpeedIT documentation build configuration file..
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this file.
#
from inspect import (
   getfile as inspect_getfile,
   currentframe as inspect_currentframe,
)
from os.path import (
   abspath as path_abspath,
   dirname as path_dirname,
   join as path_join,
)
from sys import (
   path as sys_path,
)

# If extensions (or modules to document with autodoc) are in another directory, add these directories to sys.path here.
# If the directory is relative to the documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))
SCRIPT_PATH = path_dirname(path_abspath(inspect_getfile(inspect_currentframe())))
PROJECT_ROOT = path_dirname(SCRIPT_PATH)
sys_path.insert(0, SCRIPT_PATH)
sys_path.insert(0, PROJECT_ROOT)

from PySpeedIT import (
   __author__,
   __copyright__,
   SHORT_VERSION,
   __version__,
   __project_name__,
)
from PSphinxTheme.utils import set_psphinxtheme


# ===========================================================================================================================
# General configuration
# ===========================================================================================================================

# Add any Sphinx extension module names here, as strings. They can be extensions coming with Sphinx
# (named 'sphinx.ext.*') or your custom ones.
extensions = [
   'sphinx.ext.autodoc',
   'sphinx.ext.todo',

   # =====================================================================
   # PSphinxTheme's extensions

   # a collection of all "official P-SphinxTheme admonitions"
   'PSphinxTheme.ext.psphinx_admonitions',

   # replace sphinx :samp: role handler with one that allows escaped {} chars
   'PSphinxTheme.ext.escaped_samp_literals',

   # adds extra ids & classes to genindex html, for additional styling
   'PSphinxTheme.ext.index_styling',

   # add "issue" role
   # 'PSphinxTheme.ext.issue_tracker',

   # modify logo per page
   'PSphinxTheme.ext.sidebarlogo_perpag',

   # inserts any link entries into the navigation bar (``relbar``)
   'PSphinxTheme.ext.relbar_links',

   # allow table column alignment styling
   'PSphinxTheme.ext.table_styling',
]

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'contents'

# The front page document.
index_doc = 'index'

# General information about the project
project = __project_name__
author = __author__
# noinspection PyShadowingBuiltins
copyright = __copyright__


# The version info for the project you're documenting, acts as replacement for |version| and |release|,
# also used in various other places throughout the built documents.
#
# The short X.Y version.
version = SHORT_VERSION
# The full version, including alpha/beta/rc tags.
release = __version__

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['PySpeedIT.']


# ===========================================================================================================================
# Options for all output
# ===========================================================================================================================
todo_include_todos = True
keep_warnings = True

# ===========================================================================================================================
# Set Theme and Options for HTML output
# ===========================================================================================================================

# set_psphinxtheme: html_theme_path, html_theme, needs_sphinx
html_theme_path, html_theme, needs_sphinx = set_psphinxtheme('p-main_theme')

# [optional] overwrite some of the default options
# html_theme_options = {}
# html_theme_options.update(roottarget=index_doc,
#    lighter_decor=True,
# )

# [optional] Add custom sidebar templates, maps document names to template names.
# common_sidebars = ['quicklinks.html', 'sourcelink.html', 'searchbox.html']
# html_sidebars = {
#    '**': ['localtoc.html', 'relations.html'] + common_sidebars,
#    'py-modindex': common_sidebars,
#    'genindex': common_sidebars,
#    'search': common_sidebars,
# }

# The name of an image file (relative to this directory) to place at the top of the sidebar.
html_logo = path_join('_static', 'PySpeedIT180_95_logo.png')
# The name of an image file (within the static path) to use as favicon of the docs.
# This file should be a Windows icon file (.ico) being 16x16 or 32x32 pixels large.
html_favicon = path_join('_static', 'P-Projects32_32.ico')


# The api document: extension: relbar_links
relbar_links_doc = [
   ('toc', 'contents'),
   ('api', 'api'),
]

# modify logo per page: using: P-Sphinx Theme extension: sidebarlogo_perpag
sidebarlogo_perpage_dict = {
   None: ['api', 'index', 'copyright'],
   'PySpeedIT180_95_logo_bg.png': ['RequiredSoftware', 'install', 'history', 'py-modindex', 'genindex'],
}

# The name for this set of Sphinx documents.  If None, it defaults to "<project> v<release> documentation".
html_title = '{} v{} Documentation'.format(project, release)

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = html_title

# Add any paths that contain custom static files (such as style sheets) here, relative to this directory.
# They are copied  after the builtin static files, so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If true, SmartyPants will be used to convert quotes and dashes to typographically correct entities.
html_use_smartypants = True

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom, using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# If false, no module index is generated.
html_domain_indices = True

# If false, no index is generated.
html_use_index = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr'
html_search_language = 'en'

# Output file base name for HTML help builder.
htmlhelp_basename = project + 'Doc'
