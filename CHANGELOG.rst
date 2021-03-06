===============
Release History
===============


.. _whats-new:

Version 1.0.8     2014-10-04
============================

Fixes/Other Changes:
--------------------

   - updated requirement:

      - PSphinxTheme>=2.0.1
      - psutil>=2.1.3

   - updated: Required Software


Version 1.0.7     2014-10-01
============================

Fixes/Other Changes:
--------------------

   - updated tested python version to: 3.4.2rc1
   - Required Software: setuptools >= 6.0.2
   - updated requirement: PSphinxTheme>=2.0.0


Version 1.0.6     2014-09-26
============================

Fixes/Other Changes:
--------------------

   - updated missing psutil version


Version 1.0.5     2014-09-26
============================

Features:
---------

   - `Benchmark-It` supports to use the slowest function as base in ranking


Version 1.0.4     2014-09-15
============================

Fixes/Other Changes:
--------------------

   - renamed tests module to use lower case names


Version 1.0.3     2014-09-13
============================

Fixes/Other Changes:
--------------------

   - updated requirements: fixes theme problem
   - adjusted docs/RequiredSoftware.rst


Version 1.0.2     2014-09-12
============================

Fixes/Other Changes:
--------------------

   - updated requirements
   - adjusted: README.rst


Version 1.0.1     2014-09-11
============================

Features:
---------

Fixes/Other Changes:
--------------------

   - some adjustments in setup.py
   - some documentation reformatting in utils.py
   - updated requirements
   - adjusted ``.. code-block:: python`` to ``.. code-block:: python3``


Version 1.0.0     2014-09-04
============================

Features:
---------

   - renamed project: SpeedIT to PySpeedIT
   - output is written to html files
   - simplified usage: only one interface through one function: ``PySpeedIT.speed_it.speed_it``

      - uses now option: ``html_output_dir_path`` and handles the rest internally
      - splits output into separate files per module
      - Benchmark-IT uses now a proper option for output of source-code


Fixes/Other Changes:
--------------------

   - fixed an Error in ``benchmark_it`` when a function had a default keyword argument but not input data was supplied

   - removed dependencies
      sphinxcontrib-napoleon
      Sphinx (this is pulled in by the new: PSphinxTheme)

   - added new dependencies
      PSphinxTheme
      Cython

   - added missing license for: memory_profiler


Project start 2014-05-15
========================

   - project start (named: SpeedIT)
