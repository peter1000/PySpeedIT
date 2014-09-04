"""
==============
The Versioneer
==============

CHANGES: peter1000, https://github.com/peter1000
================================================

20140731:

- addition to  __init__.py: use project import not relative imports
- changed indent to projects 3 spaces style
- changes: to fit a bit more the own Project style: example renamed ClassNames
- changes: removed check for: win32


Version: 0.11
=============

* like a rocketeer, but for versions!
* https://github.com/warner/python-versioneer
* Brian Warner
* License: Public Domain

This is a tool for managing a recorded version number in distutils-based python projects.
The goal is to remove the tedious and error-prone 'update the embedded version string' step from your release process.
Making a new release should be as easy as recording a new tag in your version-control system, and maybe making new tarballs.


Version Identifiers
-------------------

Source trees come from a variety of places:

* a version-control system checkout (mostly used by developers)
* a nightly tarball, produced by build automation
* a snapshot tarball, produced by a web-based VCS browser, like github's 'tarball from tag' feature
* a release tarball, produced by 'setup.py sdist', distributed through PyPI

Within each source tree, the version identifier (either a string or a number, this tool is format-agnostic) can come from a
variety of places:

* ask the VCS tool itself, e.g. 'git describe' (for checkouts), which knows about recent 'tags' and an absolute revision-id
* the name of the directory into which the tarball was unpacked
* an expanded VCS keyword ($Id$, etc)
* a `_version.py` created by some earlier build step

For released software, the version identifier is closely related to a VCS tag. Some projects use tag names that include more
than just the version string (e.g. 'my_project-1.2' instead of just '1.2'), in which case the tool needs to strip the tag
prefix to extract the version identifier. For unreleased software (between tags), the version identifier should provide
enough information to help developers recreate the same tree, while also giving them an idea of roughly how old the tree is
(after version 1.2, before version 1.3).

Many VCS systems can report a description that captures this, for example 'git describe --tags --dirty --always' reports
things like '0.7-1-g574ab98-dirty' to indicate that the checkout is one revision past the 0.7 tag, has a unique revision id
of '574ab98', and is 'dirty' (it has uncommitted changes.)

The version identifier is used for multiple purposes:

* to allow the module to self-identify its version: `my_project.__version__`
* to choose a name and prefix for a 'setup.py sdist' tarball


Theory of Operation
-------------------

Versioneer works by adding a special `_version.py` file into your source tree, where your `__init__.py` can import it.
This `_version.py` knows how to dynamically ask the VCS tool for version information at import time. However, when you use
'setup.py build' or 'setup.py sdist', `_version.py` in the new copy is replaced by a small static file that contains just the
generated version data.

`_version.py` also contains `$Revision$` markers, and the installation process marks `_version.py` to have this marker
rewritten with a tag name during the 'git archive' command. As a result, generated tarballs will contain enough information
to get the proper version.


Installation
------------

First, decide on values for the following configuration variables:

* `VCS`: the version control system you use. Currently accepts 'git'.

* `versionfile_source`:

   A project-relative pathname into which the generated version strings should be written. This is usually a `_version.py`
   next to your project's main `__init__.py` file. If your project uses `src/my_project/__init__.py`, this should be
   `src/my_project/_version.py`. This file should be checked in to your VCS as usual: the copy created below by `setup.py
   versioneer` will include code that parses expanded VCS keywords in generated tarballs. The 'build' and 'sdist' commands
   will replace it with a copy that has just the calculated version string.

*   `versionfile_build`:

   Like `versionfile_source`, but relative to the build directory instead of the source directory. These will differ when
   your setup.py uses 'package_dir='. If you have `package_dir={'my_project': 'src/my_project'}`, then you will probably have
   `versionfile_build='my_project/_version.py'` and `versionfile_source='src/my_project/_version.py'`.

* `tag_prefix`:

   a string, like 'PROJECTNAME-', which appears at the start of all VCS tags. If your tags look like 'my_project-1.2.0', then
   you should use tag_prefix='my_project-'. If you use unprefixed tags like '1.2.0', this should be an empty string.

* `parentdir_prefix`:

   a string, frequently the same as tag_prefix, which appears at the start of all unpacked tarball filenames. If your tarball
   unpacks into 'my_project-1.2.0', this should be 'my_project-'.


To versioneer-enable your project:
----------------------------------

* 1: Copy `versioneer.py` into the top of your source tree.

* 2: add the following lines to the top of your `setup.py`, with the configuration values you decided earlier::

   import versioneer
   versioneer.VCS = 'git'
   versioneer.versionfile_source = 'src/my_project/_version.py'
   versioneer.versionfile_build = 'my_project/_version.py'
   versioneer.tag_prefix = '' # tags are like 1.2.0
   versioneer.parentdir_prefix = 'my_project-' # dirname like 'my_project-1.2.0'

* 3: add the following arguments to the setup() call in your setup.py::

   version=versioneer.get_version(),
   cmdclass=versioneer.get_cmdclass(),

* 4: now run `setup.py versioneer`, which will create `_version.py`, and will modify your `__init__.py` to define
   `__version__` (by calling a function from `_version.py`). It will also modify your `MANIFEST.in` to include both
   `versioneer.py` and the generated `_version.py` in sdist tarballs.

* 5: commit these changes to your VCS. To make sure you won't forget, `setup.py versioneer` will mark everything it touched
   for addition.


Post-Installation Usage
-----------------------

Once established, all uses of your tree from a VCS checkout should get the current version string. All generated tarballs
should include an embedded version string (so users who unpack them will not need a VCS tool installed).

If you distribute your project through PyPI, then the release process should boil down to two steps:

* 1: git tag 1.0
* 2: python setup.py register sdist upload

If you distribute it through github (i.e. users use github to generate tarballs with `git archive`), the process is:

* 1: git tag 1.0
* 2: git push; git push --tags

Currently, all version strings must be based upon a tag. Versioneer will report 'unknown' until your tree has at least one
tag in its history. This restriction will be fixed eventually (see issue #12).


Version-String Flavors
----------------------

Code which uses Versioneer can learn about its version string at runtime by importing `version` from your main `__init__.py`
file and running the `get_versions()` function. From the 'outside' (e.g. in `setup.py`), you can   import the top-level
`versioneer.py` and run `get_versions()`.

Both functions return a dictionary with different keys for different flavors of the version string:

* `['version']`: condensed tag+distance+ shortid+dirty identifier. For git, this uses the output of
   `git describe --tags --dirty --always` but strips the tag_prefix. For example '0.11-2-g1076c97-dirty' indicates that the
   tree is like the '1076c97' commit but has uncommitted changes ('-dirty'), and that this commit is two revisions ('-2-')
   beyond the '0.11' tag. For released software (exactly equal to a known tag), the identifier will only contain the stripped
   tag, e.g. '0.11'.

* `['full']`: detailed revision identifier. For Git, this is the full SHA1 commit id, followed by '-dirty' if the tree
   contains uncommitted changes, e.g. '1076c978a8d3cfc70f408fe5974aa6c092c949ac-dirty'.

Some variants are more useful than others. Including `full` in a bug report should allow developers to reconstruct the exact
code being tested (or indicate the presence of local changes that should be shared with the developers). `version` is
suitable for display in an 'about' box or a CLI `--version` output: it can be easily compared against release notes and lists
of bugs fixed in various releases.

In the future, this will also include a [PEP-0440](http://legacy.python.org/dev/peps/pep-0440/) -compatible flavor
(e.g. `1.2.post0.dev123`). This loses a lot of information (and has no room for a hash-based revision id), but is safe to use
in a `setup.py` '`version=`' argument. It also enables tools like *pip* to compare version strings and evaluate
compatibility constraint declarations.

The `setup.py versioneer` command adds the following text to your `__init__.py` to place a basic version
in `YOUR_PROJECT.__version__`::

   from PySpeedIT.version import get_versions
   __version__ = get_versions()['version']
   del get_versions


Updating Versioneer
-------------------

To upgrade your project to a new release of Versioneer, do the following:

* install the new Versioneer (`pip install -U versioneer` or equivalent)
* re-run `versioneer-installer` in your source tree to replace your copy of `versioneer.py`
* edit `setup.py`, if necessary, to include any new configuration settings indicated by the release notes
* re-run `setup.py versioneer` to replace `SRC/_version.py`
* commit any changed files


Upgrading from 0.10 to 0.11
---------------------------

You must add a `versioneer.VCS = 'git'` to your `setup.py` before re-running `setup.py versioneer`. This will enable the use
of additional version-control systems (SVN, etc) in the future.


Future Directions
-----------------

This tool is designed to make it easily extended to other version-control systems: all VCS-specific components are in
separate directories like src/git/ . The top-level `versioneer.py` script is assembled from these components by running
make-versioneer.py . In the future, make-versioneer.py will take a VCS name as an argument, and will construct a version of
`versioneer.py` that is specific to the given VCS. It might also take the configuration arguments that are currently provided
manually during installation by editing setup.py . Alternatively, it might go the other direction and include code from all
supported VCS systems, reducing the number of intermediate scripts.


License
-------
To make Versioneer easier to embed, all its code is hereby released into the public domain. The `_version.py` that it creates
is also in the public domain.

"""
from distutils.core import Command
from distutils.command.sdist import sdist as _sdist
from distutils.command.build import build as _build
from errno import ENOENT as ERRNO_ENOENT
from os import (
   unlink as os_unlink,
)
from os.path import (
   abspath as path_abspath,
   basename as path_basename,
   dirname as path_dirname,
   exists as path_exists,
   join as path_join,
   relpath as path_relpath,
   splitext as path_splitext,
)
from re import (
   search as re_search,
   match as re_match,
)
# noinspection PyPep8Naming
from subprocess import (
   Popen as subprocess_Popen,
   PIPE as subprocess_PIPE,
)
from sys import (
   argv as sys_argv,
   exc_info as sys_exc_info,
   modules as sys_modules,
   version as sys_version,
)


# these dictionaries contain VCS-specific tools
# noinspection PyDictCreation
LONG_VERSION_PY = {}

LONG_VERSION_PY['git'] = '''
# pylint: skip-file
#
# This file helps to compute a version number in source trees obtained from:
#
# git-archive tarball (such as those provided by githubs download-from-tag feature).
#
#  Distribution tarballs (built by setup.py sdist) and build directories (produced by setup.py build) will contain a much
#  shorter file that just contains the computed version number.
#
# This file is released into the public domain.
# Generated by versioneer-0.11 (https://github.com/warner/python-versioneer)
#
#
# CHANGES: peter1000, https://github.com/peter1000
# ================================================
#
# 20140731:
#
# - addition to  __init__.py: use project import not relative imports
# - changed indent to projects 3 spaces style
# - changes: to fit a bit more the own Project style: example renamed ClassNames
# - changes: removed check for: win32
#
from errno import ENOENT
from os import sep as os_sep
from os.path import (
   abspath as path_abspath,
   basename as path_basename,
   dirname as path_dirname,
   exists as path_exists,
   join as path_join,
)
from re import search as re_search
from subprocess import (
   Popen as subprocess_Popen,
   PIPE,
)
from sys import (
   exc_info as sys_exc_info,
   version as sys_version,
)


# these strings will be replaced by git during git-archive
git_refnames = '%(DOLLAR)sFormat:%%d%(DOLLAR)s'
git_full = '%(DOLLAR)sFormat:%%H%(DOLLAR)s'

# these strings are filled in when 'setup.py versioneer' creates _version.py
tag_prefix = '%(TAG_PREFIX)s'
parentdir_prefix = '%(PARENTDIR_PREFIX)s'
versionfile_source = '%(VERSIONFILE_SOURCE)s'


def run_command(commands, args, cwd=None, verbose=False, hide_stderr=False):
   assert isinstance(commands, list)
   # noinspection PyUnusedLocal
   p = None
   for c in commands:
      try:
         p = subprocess_Popen([c] + args, cwd=cwd, stdout=PIPE, stderr=(PIPE if hide_stderr else None))
         break
      except EnvironmentError:
         e = sys_exc_info()[1]
         if e.errno == ENOENT:
            continue
         if verbose:
            print('unable to run {}'.format(args[0]))
            print(e)
         return None
   else:
      if verbose:
         print('unable to find command, tried {}'.format(commands))
      return None
   stdout = p.communicate()[0].strip()
   if sys_version >= '3':
      stdout = stdout.decode()
   if p.returncode != 0:
      if verbose:
         print('unable to run {} (error)'.format(args[0]))
      return None
   return stdout


def versions_from_parentdir(_parentdir_prefix, root, verbose=False):
   # Source tarballs conventionally unpack into a directory that includes both the project name and a version string.
   dirname = path_basename(root)
   if not dirname.startswith(_parentdir_prefix):
      if verbose:
         print('guessing rootdir is <{}>, but <{}> does not start with prefix <{}>'.format(root, dirname, _parentdir_prefix))
      return None
   return {'version': dirname[len(_parentdir_prefix):], 'full': ''}


def git_get_keywords(versionfile_abs):
   # the code embedded in _version.py can just fetch the value of these keywords. When used from setup.py, we don't want to
   # import _version.py, so we do it with a regexp instead. This function is not used from _version.py.
   keywords = {}
   try:
      f = open(versionfile_abs, 'r')
      for line in f.readlines():
         if line.strip().startswith('git_refnames ='):
            mo = re_search(r'=\s*"(.*)"', line)
            if mo:
               keywords['refnames'] = mo.group(1)
         if line.strip().startswith('git_full ='):
            mo = re_search(r'=\s*"(.*)"', line)
            if mo:
               keywords['full'] = mo.group(1)
      f.close()
   except EnvironmentError:
      pass
   return keywords


def git_versions_from_keywords(keywords, _tag_prefix, verbose=False):
   if not keywords:
      return {}  # keyword-finding function failed to find keywords
   refnames = keywords['refnames'].strip()
   if refnames.startswith('$Format'):
      if verbose:
         print('keywords are unexpanded, not using')
      return {}  # unexpanded, so not in an unpacked git-archive tarball
   refs = set([r.strip() for r in refnames.strip('()').split(',')])
   # starting in git-1.8.3, tags are listed as 'tag: foo-1.0' instead of just 'foo-1.0'. If we see a 'tag: ' prefix, prefer
   # those.

   # noinspection PyPep8Naming
   TAG = 'tag: '
   tags = set([r[len(TAG):] for r in refs if r.startswith(TAG)])
   if not tags:
      # Either we're using git < 1.8.3, or there really are no tags. We use a heuristic: assume all version tags have a
      # digit. The old git `percentage d` expansion behaves like git log --decorate=short and strips out the refs/heads/ and
      # refs/tags/ prefixes that would let us distinguish between branches and tags. By ignoring refnames without digits, we
      # filter out many common branch names like 'release' and 'stabilization', as well as 'HEAD' and 'master'.
      tags = set([r for r in refs if re_search(r'\d', r)])
      if verbose:
         print('discarding <{}>, no digits'.format(','.join(refs - tags)))
   if verbose:
      print('likely tags: {}'.format(','.join(sorted(tags))))
   for ref in sorted(tags):
      # sorting will prefer e.g. '2.0' over '2.0rc1'
      if ref.startswith(_tag_prefix):
         r = ref[len(_tag_prefix):]
         if verbose:
            print('picking {}'.format(r))
         return {'version': r, 'full': keywords['full'].strip()}
   # no suitable tags, so we use the full revision id
   if verbose:
      print('no suitable tags, using full revision id')
   return {'version': keywords['full'].strip(), 'full': keywords['full'].strip()}


def git_versions_from_vcs(_tag_prefix, root, verbose=False):
   # this runs 'git' from the root of the source tree. This only gets called if the git-archive 'subst' keywords were *not*
   # expanded, and _version.py hasn't already been rewritten with a short version string, meaning we're inside a checked out
   # source tree.
   if not path_exists(path_join(root, '.git')):
      if verbose:
         print('no .git in {}'.format(root))
      return {}

   # noinspection PyPep8Naming
   GITS = ['git']
   stdout = run_command(GITS, ['describe', '--tags', '--dirty', '--always'], cwd=root)
   if stdout is None:
      return {}
   if not stdout.startswith(_tag_prefix):
      if verbose:
         print('tag <{}> does not start with prefix <{}>'.format(stdout, _tag_prefix))
      return {}
   tag = stdout[len(_tag_prefix):]
   stdout = run_command(GITS, ['rev-parse', 'HEAD'], cwd=root)
   if stdout is None:
      return {}
   full = stdout.strip()
   if tag.endswith('-dirty'):
      full += '-dirty'
   return {'version': tag, 'full': full}


def get_versions(default=None, verbose=False):
   # I am in _version.py, which lives at ROOT/VERSIONFILE_SOURCE. If we have __file__, we can work backwards from there to
   # the root. Some py2exe/bbfreeze/non-CPython implementations don't do __file__, in which case we can only use expanded
   # keywords.
   if not default:
      default = {'version': 'unknown', 'full': ''}
   keywords = {'refnames': git_refnames, 'full': git_full}
   ver = git_versions_from_keywords(keywords, tag_prefix, verbose)
   if ver:
      return ver

   try:
      root = path_abspath(__file__)
      # versionfile_source is the relative path from the top of the source tree (where the .git directory might live) to this
      # file. Invert this to find the root from __file__.
      for i in range(len(versionfile_source.split(os_sep))):
         root = path_dirname(root)
   except NameError:
      return default

   return (
      git_versions_from_vcs(tag_prefix, root, verbose)
      or versions_from_parentdir(parentdir_prefix, root, verbose)
      or default
   )
'''

SHORT_VERSION_PY = '''
# This file was generated by 'versioneer.py' (0.11) from revision-control system data, or from the parent directory name of
# an unpacked source archive. Distribution tarballs contain a pre-generated copy of this file.

version_version = '%(version)s'
version_full = '%(full)s'
def get_versions(default={}, verbose=False):
   return {'version': version_version, 'full': version_full}
'''

INIT_PY_SNIPPET = '''from PySpeedIT._version import get_versions
__version__ = get_versions()['version']
del get_versions'''

DEFAULT = {'version': 'unknown', 'full': 'unknown'}


# these configuration settings will be overridden by setup.py after it imports us
versionfile_source = None
versionfile_build = None
tag_prefix = None
parentdir_prefix = None
VCS = None


def run_command(commands, args, cwd=None, verbose=False, hide_stderr=False):
   assert isinstance(commands, list)
   # noinspection PyUnusedLocal
   p = None
   for c in commands:
      try:
         # remember shell=False, so use git.cmd on windows, not just git
         p = subprocess_Popen([c] + args, cwd=cwd, stdout=subprocess_PIPE, stderr=(subprocess_PIPE if hide_stderr else None))
         break
      except EnvironmentError:
         e = sys_exc_info()[1]
         if e.errno == ERRNO_ENOENT:
            continue
         if verbose:
            print('unable to run {}'.format(args[0]))
            print(e)
         return None
   else:
      if verbose:
         print('unable to find command, tried {}'.format(commands, ))
      return None
   stdout = p.communicate()[0].strip()
   if sys_version >= '3':
      stdout = stdout.decode()
   if p.returncode != 0:
      if verbose:
         print('unable to run {} (error)'.format(args[0]))
      return None
   return stdout


def git_get_keywords(versionfile_abs):
   # the code embedded in _version.py can just fetch the value of these keywords. When used from setup.py, we don't want to
   # import _version.py, so we do it with a regexp instead. This function is not used from _version.py.
   keywords = {}
   try:
      f = open(versionfile_abs, 'r')
      for line in f.readlines():
         if line.strip().startswith('git_refnames ='):
            mo = re_search(r'=\s*"(.*)"', line)
            if mo:
               keywords['refnames'] = mo.group(1)
         if line.strip().startswith('git_full ='):
            mo = re_search(r'=\s*"(.*)"', line)
            if mo:
               keywords['full'] = mo.group(1)
      f.close()
   except EnvironmentError:
      pass
   return keywords


def git_versions_from_keywords(keywords, tag_prefix_, verbose=False):
   if not keywords:
      return {}  # keyword-finding function failed to find keywords
   refnames = keywords['refnames'].strip()
   if refnames.startswith('$Format'):
      if verbose:
         print('keywords are unexpanded, not using')
      return {}  # unexpanded, so not in an unpacked git-archive tarball
   refs = set([r.strip() for r in refnames.strip('()').split(',')])
   # starting in git-1.8.3, tags are listed as 'tag: foo-1.0' instead of just 'foo-1.0'. If we see a 'tag: ' prefix, prefer
   # those.
   # noinspection PyPep8Naming
   TAG = 'tag: '
   tags = set([r[len(TAG):] for r in refs if r.startswith(TAG)])
   if not tags:
      # Either we're using git < 1.8.3, or there really are no tags. We use a heuristic: assume all version tags have a
      # digit. The old git %d expansion behaves like git log --decorate=short and strips out the refs/heads/ and refs/tags/
      # prefixes that would let us distinguish between branches and tags. By ignoring refnames without digits, we filter out
      # many common branch names like 'release' and 'stabilization', as well as 'HEAD' and 'master'.
      tags = set([r for r in refs if re_search(r'\d', r)])
      if verbose:
         print('discarding <{}>, no digits'.format(','.join(refs - tags)))
   if verbose:
      print('likely tags: {}'.format(','.join(sorted(tags))))
   for ref in sorted(tags):
      # sorting will prefer e.g. '2.0' over '2.0rc1'
      if ref.startswith(tag_prefix_):
         r = ref[len(tag_prefix_):]
         if verbose:
            print('picking {}'.format(r))
         return {'version': r, 'full': keywords['full'].strip()}
   # no suitable tags, so we use the full revision id
   if verbose:
      print('no suitable tags, using full revision id')
   return {'version': keywords['full'].strip(), 'full': keywords['full'].strip()}


def git_versions_from_vcs(tag_prefix_, root, verbose=False):
   # this runs 'git' from the root of the source tree. This only gets called if the git-archive 'subst' keywords were *not*
   # expanded, and _version.py hasn't already been rewritten with a short version string, meaning we're inside a checked out
   # source tree.

   if not path_exists(path_join(root, '.git')):
      if verbose:
         print('no .git in {}'.format(root))
      return {}

   # noinspection PyPep8Naming
   GITS = ['git']
   stdout = run_command(GITS, ['describe', '--tags', '--dirty', '--always'], cwd=root)
   if stdout is None:
      return {}
   if not stdout.startswith(tag_prefix_):
      if verbose:
         print('tag <{}> does not start with prefix <{}>'.format(stdout, tag_prefix_))
      return {}
   tag = stdout[len(tag_prefix_):]
   stdout = run_command(GITS, ['rev-parse', 'HEAD'], cwd=root)
   if stdout is None:
      return {}
   full = stdout.strip()
   if tag.endswith('-dirty'):
      full += '-dirty'
   return {'version': tag, 'full': full}


def do_vcs_install(manifest_in, versionfile_source_, ipy):
   # noinspection PyPep8Naming
   GITS = ['git']
   files = [manifest_in, versionfile_source_, ipy]
   try:
      me = __file__
      if me.endswith('.pyc') or me.endswith('.pyo'):
         me = path_splitext(me)[0] + '.py'
      versioneer_file = path_relpath(me)
   except NameError:
      versioneer_file = 'versioneer.py'
   files.append(versioneer_file)
   present = False
   try:
      f = open('.gitattributes', 'r')
      for line in f.readlines():
         if line.strip().startswith(versionfile_source_):
            if 'export-subst' in line.strip().split()[1:]:
               present = True
      f.close()
   except EnvironmentError:
      pass
   if not present:
      f = open('.gitattributes', 'a+')
      f.write('{} export-subst\n'.format(versionfile_source_))
      f.close()
      files.append('.gitattributes')
   run_command(GITS, ['add', '--'] + files)


def versions_from_parentdir(parentdir_prefix_, root, verbose=False):
   # Source tarballs conventionally unpack into a directory that includes both the project name and a version string.
   dirname = path_basename(root)
   if not dirname.startswith(parentdir_prefix_):
      if verbose:
         print('guessing rootdir is <{}>, but <{}> does not start with prefix <{}>'.format(root, dirname, parentdir_prefix_))
      return None
   return {'version': dirname[len(parentdir_prefix_):], 'full': ''}


def versions_from_file(filename):
   versions = {}
   try:
      with open(filename) as f:
         for line in f.readlines():
            mo = re_match("version_version = '([^']+)'", line)
            if mo:
               versions['version'] = mo.group(1)
            mo = re_match("version_full = '([^']+)'", line)
            if mo:
               versions['full'] = mo.group(1)
   except EnvironmentError:
      return {}

   return versions


def write_to_version_file(filename, versions):
   with open(filename, 'w') as f:
      f.write(SHORT_VERSION_PY % versions)

   print('set {} to <{}>'.format(filename, versions['version']))


def get_root():
   try:
      return path_dirname(path_abspath(__file__))
   except NameError:
      return path_dirname(path_abspath(sys_argv[0]))


def vcs_function(vcs, suffix):
   return getattr(sys_modules[__name__], '{}_{}'.format(vcs, suffix), None)


def get_versions(default=DEFAULT, verbose=False):
   # returns dict with two keys: 'version' and 'full'
   assert versionfile_source is not None, 'please set versioneer.versionfile_source'
   assert tag_prefix is not None, 'please set versioneer.tag_prefix'
   assert parentdir_prefix is not None, 'please set versioneer.parentdir_prefix'
   assert VCS is not None, 'please set versioneer.VCS'

   # I am in versioneer.py, which must live at the top of the source tree, which we use to compute the root directory.
   # py2exe/bbfreeze/non-CPython don't have __file__, in which case we fall back to sys.argv[0] (which ought to be the
   # setup.py script). We prefer __file__ since that's more robust in cases where setup.py was invoked in some weird way
   # (e.g. pip)
   root = get_root()
   versionfile_abs = path_join(root, versionfile_source)

   # extract version from first of _version.py, VCS command (e.g. 'git describe'), parentdir. This is meant to work for
   # developers using a source checkout, for users of a tarball created by 'setup.py sdist', and for users of a tarball/zip
   # ball created by 'git archive' or github's download-from-tag feature or the equivalent in other VCSes.

   get_keywords_f = vcs_function(VCS, 'get_keywords')
   versions_from_keywords_f = vcs_function(VCS, 'versions_from_keywords')
   if get_keywords_f and versions_from_keywords_f:
      vcs_keywords = get_keywords_f(versionfile_abs)
      ver = versions_from_keywords_f(vcs_keywords, tag_prefix)
      if ver:
         if verbose:
            print('got version from expanded keyword {}'.format(ver))
         return ver

   ver = versions_from_file(versionfile_abs)
   if ver:
      if verbose:
         print('got version from file {} {}'.format(versionfile_abs, ver))
      return ver

   versions_from_vcs_f = vcs_function(VCS, 'versions_from_vcs')
   if versions_from_vcs_f:
      ver = versions_from_vcs_f(tag_prefix, root, verbose)
      if ver:
         if verbose:
            print('got version from VCS {}'.format(ver))
         return ver

   ver = versions_from_parentdir(parentdir_prefix, root, verbose)
   if ver:
      if verbose:
         print('got version from parentdir {}'.format(ver))
      return ver

   if verbose:
      print('got version from default {}'.format(default))
   return default


def get_version(verbose=False):
   return get_versions(verbose=verbose)['version']


class CmdVersion(Command):
   description = 'report generated version string'
   user_options = []
   boolean_options = []

   def initialize_options(self):
      pass

   def finalize_options(self):
      pass

   def run(self):
      ver = get_version(verbose=True)
      print('Version is currently: {}'.format(ver))


class CmdBuild(_build):
   def run(self):
      versions = get_versions(verbose=True)
      _build.run(self)
      # now locate _version.py in the new build/ directory and replace it with an updated value
      target_versionfile = path_join(self.build_lib, versionfile_build)
      print('UPDATING {}'.format(target_versionfile))
      os_unlink(target_versionfile)
      with open(target_versionfile, 'w') as file_:
         file_.write(SHORT_VERSION_PY % versions)


if 'cx_Freeze' in sys_modules:  # cx_freeze enabled?
   # noinspection PyPackageRequirements,PyUnresolvedReferences
   from cx_Freeze.dist import build_exe as _build_exe

   class CmdBuildExe(_build_exe):
      def run(self):
         versions = get_versions(verbose=True)
         target_versionfile = versionfile_source
         print('UPDATING {}'.format(target_versionfile))
         os_unlink(target_versionfile)
         with open(target_versionfile, 'w') as f:
            f.write(SHORT_VERSION_PY % versions)

         _build_exe.run(self)
         os_unlink(target_versionfile)
         # noinspection PyTypeChecker
         with open(versionfile_source, 'w') as f:
            assert VCS is not None, 'please set versioneer.VCS'
            # noinspection PyPep8Naming
            LONG = LONG_VERSION_PY[VCS]
            f.write(LONG % {
               'DOLLAR': '$',
               'TAG_PREFIX': tag_prefix,
               'PARENTDIR_PREFIX': parentdir_prefix,
               'VERSIONFILE_SOURCE': versionfile_source,
            })


class CmdSdist(_sdist):
   def run(self):
      versions = get_versions(verbose=True)
      # noinspection PyAttributeOutsideInit
      self._versioneer_generated_versions = versions
      # unless we update this, the command will keep using the old version
      self.distribution.metadata.version = versions['version']
      return _sdist.run(self)


   def make_release_tree(self, base_dir, files):
      _sdist.make_release_tree(self, base_dir, files)
      # now locate _version.py in the new base_dir directory (remembering that it may be a hardlink) and replace it with an
      # updated value
      target_versionfile = path_join(base_dir, versionfile_source)
      print('UPDATING {}'.format(target_versionfile))
      os_unlink(target_versionfile)
      with open(target_versionfile, 'w') as f:
         f.write(SHORT_VERSION_PY % self._versioneer_generated_versions)


class CmdUpdateFiles(Command):
   description = 'install/upgrade Versioneer files: __init__.py SRC/_version.py'
   user_options = []
   boolean_options = []

   def initialize_options(self):
      pass

   def finalize_options(self):
      pass

   # noinspection PyPep8Naming
   def run(self):
      print(' creating {}'.format(versionfile_source))
      # noinspection PyTypeChecker
      with open(versionfile_source, 'w') as file_:
         assert VCS is not None, 'please set versioneer.VCS'
         LONG = LONG_VERSION_PY[VCS]
         file_.write(LONG % {
            'DOLLAR': '$',
            'TAG_PREFIX': tag_prefix,
            'PARENTDIR_PREFIX': parentdir_prefix,
            'VERSIONFILE_SOURCE': versionfile_source,
         })

      # noinspection PyTypeChecker
      ipy = path_join(path_dirname(versionfile_source), '__init__.py')
      try:
         with open(ipy, 'r') as file_:
            old = file_.read()
      except EnvironmentError:
         old = ''
      if INIT_PY_SNIPPET not in old:
         print(' appending to {}'.format(ipy))
         with open(ipy, 'a') as file_:
            file_.write(INIT_PY_SNIPPET)
      else:
         print(' {} unmodified'.format(ipy))

      # Make sure both the top-level 'versioneer.py' and versionfile_source (PKG/_version.py, used by runtime code) are in
      # MANIFEST.in, so they'll be copied into source distributions. Pip won't be able to install the package without this.
      manifest_in = path_join(get_root(), 'MANIFEST.in')
      simple_includes = set()
      try:
         with open(manifest_in, 'r') as file_:
            for line in file_:
               if line.startswith('include '):
                  for include in line.split()[1:]:
                     simple_includes.add(include)
      except EnvironmentError:
         pass
      # That doesn't cover everything MANIFEST.in can do (http://docs.python.org/2/distutils/sourcedist.html#commands), so it
      # might give some false negatives. Appending redundant 'include' lines is safe, though.
      if 'versioneer.py' not in simple_includes:
         print(' appending <versioneer.py> to MANIFEST.in')
         with open(manifest_in, 'a') as file_:
            file_.write('include versioneer.py\n')
      else:
         print(' <versioneer.py> already in MANIFEST.in')
      if versionfile_source not in simple_includes:
         print(' appending versionfile_source: <{}> to MANIFEST.in'.format(versionfile_source))
         with open(manifest_in, 'a') as file_:
            file_.write('include {}\n'.format(versionfile_source))
      else:
         print(' versionfile_source already in MANIFEST.in')

      # Make VCS-specific changes. For git, this means creating/changing `.gitattributes` to mark _version.py for export-time
      # keyword substitution.
      do_vcs_install(manifest_in, versionfile_source, ipy)


def get_cmdclass():
   cmds = {
      'version': CmdVersion,
      'versioneer': CmdUpdateFiles,
      'build': CmdBuild,
      'sdist': CmdSdist,
   }
   if 'cx_Freeze' in sys_modules:  # cx_freeze enabled?
      cmds['build_exe'] = CmdBuildExe
      del cmds['build']

   return cmds
