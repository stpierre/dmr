.. include:: defs.rst

.. _input-format:

==================
 dmr Input Format
==================

dmr expects semi-structured input written in `reStructuredText`_.
This document explains the structure of a dmr resume document; for
technical details, see the :mod:`dmr.input` API docs.

This document will include examples; for a full working example, see
`<http://github.com/stpierre/resume>`_.

.. autoclass:: dmr.data.Document
   :no-members:
   :noindex:

.. _input-address-block:

Address Block
=============

.. autoclass:: dmr.data.Contact
   :no-members:
   :noindex:

.. _input-sections:

Sections
========

The resume will be divided into any number of sections, which hold the
real data.  There are four different types of sections, most of which
are very simple:

.. _input-text:

Text
----

.. autoclass:: dmr.data.Text
   :no-members:
   :noindex:

.. _input-list:

List
----

.. autoclass:: dmr.data.List
   :no-members:
   :noindex:

.. _input-references:

References
----------

.. autoclass:: dmr.data.References
   :no-members:
   :noindex:

.. _input-experience:

Experience
----------

.. autoclass:: dmr.data.Experience
   :no-members:
   :noindex:

.. _input-job:

Job Section
===========

.. autoclass:: dmr.data.Job
   :no-members:
   :noindex:

.. _input-dates:

Date Range
==========
.. autoclass:: dmr.data.Dates
   :no-members:
   :noindex:

