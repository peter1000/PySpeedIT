

=========================
Installation Instructions
=========================

.. index:: PySpeedIT; requirements

Requirements
============
See :doc:`RequiredSoftware`.


.. index:: PySpeedIT; installation

Installing
==========

.. shell-example::

   To install from pypi using ``pip/pip3``

   .. code-block:: sh

      $ pip3 install PySpeedIT

   To install from source using ``setup.py``

   .. code-block:: sh

      $ python3 setup.py build
      $ sudo python3 setup.py install

   To install from source using ``make``

   .. code-block:: sh

      $ sudo make install

.. note::

   In the source root folder the Makefile has a number of helpful shortcut commands

.. important:: Warnings at installation

   .. code-block:: sh

      $ warning: no previously-included files matching '__pycache__' found under directory '*'

   This can be ignored `__pycache__` is excluded in the `MANIFEST.in` file

Documentation
=============
The latest copy of this documentation should always be available at: `<http://packages.python.org/PySpeedIT>`_

If you wish to generate your own copy of the documentation, you will need to:

#. Download the :mod:`!PySpeedIT` source.
#. If not already installed - install `PSphinxTheme <https://github.com/peter1000/PSphinxTheme>`_ (1.2.4 or better)

   .. code-block:: sh

      $ pip3 install PSphinxTheme

#. From the `PySpeedIT` source directory, run:

   .. shell-example::

      To build the documentation from source using ``setup.py``

      .. code-block:: sh

         $ python3 setup.py build_sphinx -E

      To build from source using ``make``

      .. code-block:: sh

         $ make docs

#. Once Sphinx is finished, point a web browser to the file :samp:`{SOURCE}/build/sphinx/html/index.html`.
