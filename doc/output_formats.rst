.. include:: defs.rst

.. _output-formats:

====================
 dmr Output Formats
====================

dmr supports several different output formats:

HTML
====

.. automodule:: dmr.output.html
   :no-members:
   :noindex:

LaTeX
=====

.. automodule:: dmr.output.latex
   :no-members:
   :noindex:

JSON
====

.. automodule:: dmr.output.json
   :no-members:
   :noindex:

Other formats
=============

Additionally, since the :ref:`input-format` is structured to look like
a resume, many of the existing ``rst2*`` tools (and other tools that
read `reST`_, like `pandoc <http://johnmacfarlane.net/pandoc/>`) will
work with little further modification.  This allows you to easily
export your resume to a variety of other formats, including XML, docx,
ODT, EPUB, and more.

