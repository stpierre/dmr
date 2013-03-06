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

.. _input-exclusions:

Exclusions
==========

Sections, jobs, and job positions -- basically, anything under a
`reST`_ section heading -- can be excluded or included for different
formats.  This lets you write a full "long form" resume that might
take several pages for presentation on a website, and publish a
shorter, two-page PDF resume with selected content only.

The simplest way to specify sections to exclude is by title.  For
instance, consider a resume with both of the following sections:

.. code-block:: rst

    References Available Upon Request
    =================================

    References
    ==========

    | Someone Reliable
    | 123 Not a Fake St.
    | Real City, XX 54321

You could generate your resume with either of the following:

.. code-block:: bash

    dmr --exclude=References
    dmr --exclude="References Available Upon Request"

You can exclude multiple sections by giving multiple ``--exclude``
options.

That could be tedious, though, especially if you have many sections
you want to exclude or include.  In that case, you can add different
sections to named section groups.  E.g.:

.. code-block:: rst

    References Available Upon Request
    =================================

    .. group short-form

    References
    ==========

    .. group long-form

    | Someone Reliable
    | 123 Not a Fake St.
    | Real City, XX 54321

Now you can run:

.. code-block:: bash

    dmr --exclude=long-form
    dmr --exclude=short-form

To take it one step further, you can ensure that your PDF resume is
always the short form by default, and otherwise your resume is always
the long form by default by using in-document configuration.  To do
so, you'd add the following to the top of the document:

.. code-block:: rst

    .. options
       exclude short-form
    .. options=latex
       exclude long-form
       include short-form

Note that includes *always* take precendence over excludes, no matter
where they're specified.  So if you have an include in
``/etc/dmr.conf``, that section cannot be excluded.  This isn't a
significant drawback in practice, because all sections are included by
default, so there's very little reason to explicitly include a section
in ``/etc/dmr.conf``.

See :ref:`configuration-global` for details on the syntax of
specifying exclude and include lists.
